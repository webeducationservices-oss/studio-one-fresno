-- Wholesale order email notifications  (StudioOne-CA Supabase project: ddeqyxmvrnqudbsdxxox)
-- ---------------------------------------------------------------------------------------
-- Fires SERVER-SIDE on every INSERT into public.wholesale_orders and emails Cat (+ Justin)
-- via Resend, using pg_net. This is independent of the browser, so an order can never be
-- placed "silently" again. The wholesale shop is a REQUEST/QUOTE flow — no payment is
-- collected; Cat arranges pricing & fulfillment with the stylist directly.
--
-- The Resend API key is stored in Supabase Vault under the name 'resend_api_key'
-- (NOT in this file, NOT in the repo). To (re)store it:
--   select vault.create_secret('<RESEND_KEY>', 'resend_api_key', 'Resend API key for wholesale order emails');
--
-- Recipients are hardcoded below: to = hairbycatb@gmail.com + studioone.lp@gmail.com,
-- bcc = justin@webeducationservices.com, reply_to = the ordering stylist.
-- Sender: noreply@studioonefresno.com (studioonefresno.com is a Resend-verified domain).

create extension if not exists pg_net;

-- Minimal HTML escaper so a stylist's product/note text can't inject markup into the email
create or replace function public.esc(t text) returns text
language sql immutable as $e$
  select replace(replace(replace(coalesce(t,''),'&','&amp;'),'<','&lt;'),'>','&gt;')
$e$;

-- Build + send one order-notification email. Reusable so missed orders can be re-sent:
--   select public.send_wholesale_order_email('<order-uuid>');
create or replace function public.send_wholesale_order_email(p_order_id uuid)
returns void
language plpgsql
security definer
set search_path = public, vault, extensions, net
as $fn$
declare
  v_key text; v_order public.wholesale_orders%rowtype;
  v_email text; v_name text; v_rows text := ''; it jsonb;
  v_total text; v_placed text; v_note text; v_html text;
begin
  select * into v_order from public.wholesale_orders where id = p_order_id;
  if not found then return; end if;

  select decrypted_secret into v_key from vault.decrypted_secrets where name='resend_api_key' limit 1;
  if v_key is null then raise exception 'resend_api_key missing from vault'; end if;

  select email, coalesce(nullif(raw_user_meta_data->>'full_name',''), email)
    into v_email, v_name from auth.users where id = v_order.user_id;
  v_email := coalesce(v_email,'unknown'); v_name := coalesce(v_name,'Unknown stylist');

  for it in select * from jsonb_array_elements(v_order.items) loop
    v_rows := v_rows ||
      '<tr>'||
      '<td style="padding:8px 12px;border-bottom:1px solid #eee">'|| public.esc(it->>'name') ||'</td>'||
      '<td style="padding:8px 12px;border-bottom:1px solid #eee;color:#555">'|| public.esc(it->>'variant') ||'</td>'||
      '<td style="padding:8px 12px;border-bottom:1px solid #eee;text-align:center">'|| public.esc(it->>'qty') ||'</td>'||
      '<td style="padding:8px 12px;border-bottom:1px solid #eee;text-align:right">$'||
        to_char((coalesce((it->>'price_cents')::int,0)*coalesce((it->>'qty')::int,0))/100.0,'FM999990.00') ||'</td>'||
      '</tr>';
  end loop;

  v_total  := to_char(coalesce(v_order.subtotal_cents,0)/100.0,'FM999990.00');
  v_placed := to_char(v_order.created_at at time zone 'America/Los_Angeles','FMMon FMDD, YYYY "at" HH12:MI AM');
  v_note   := public.esc(coalesce(nullif(v_order.note,''),'(none)'));

  v_html :=
    '<div style="font-family:Arial,Helvetica,sans-serif;max-width:600px;margin:0 auto;color:#222">'||
      '<div style="background:#4c5223;padding:20px 24px">'||
        '<p style="margin:0;color:#cfe0a8;font-size:11px;letter-spacing:2px;text-transform:uppercase">Studio One Wholesale</p>'||
        '<h1 style="margin:4px 0 0;color:#fff;font-size:22px;font-weight:600">New Order Request</h1>'||
      '</div>'||
      '<div style="padding:24px">'||
        '<p style="margin:0 0 4px"><strong>Stylist:</strong> '||public.esc(v_name)||'</p>'||
        '<p style="margin:0 0 4px"><strong>Email:</strong> '||public.esc(v_email)||'</p>'||
        '<p style="margin:0 0 18px"><strong>Placed:</strong> '||v_placed||' (PT)</p>'||
        '<table style="width:100%;border-collapse:collapse;font-size:14px">'||
          '<thead><tr style="text-align:left;color:#888;font-size:11px;text-transform:uppercase">'||
            '<th style="padding:8px 12px;border-bottom:2px solid #4c5223">Product</th>'||
            '<th style="padding:8px 12px;border-bottom:2px solid #4c5223">Length</th>'||
            '<th style="padding:8px 12px;border-bottom:2px solid #4c5223;text-align:center">Qty</th>'||
            '<th style="padding:8px 12px;border-bottom:2px solid #4c5223;text-align:right">Subtotal</th>'||
          '</tr></thead><tbody>'|| v_rows ||'</tbody>'||
          '<tfoot><tr><td colspan="3" style="padding:12px;text-align:right;font-weight:600">Total</td>'||
            '<td style="padding:12px;text-align:right;font-weight:700;font-size:16px">$'||v_total||'</td></tr></tfoot>'||
        '</table>'||
        '<div style="margin-top:18px;padding:14px 16px;background:#f6f6ef;border-left:3px solid #4c5223;border-radius:3px">'||
          '<p style="margin:0;font-size:12px;color:#888;text-transform:uppercase;letter-spacing:1px">Note from stylist</p>'||
          '<p style="margin:6px 0 0;font-size:15px">'||v_note||'</p>'||
        '</div>'||
        '<p style="margin:22px 0 0;font-size:13px;color:#666">Reply to this email to reach '||public.esc(v_name)||' directly. '||
        'This is an order <em>request</em> &mdash; no payment was collected; arrange pricing &amp; fulfillment with the stylist.</p>'||
      '</div>'||
    '</div>';

  perform net.http_post(
    url := 'https://api.resend.com/emails',
    headers := jsonb_build_object('Authorization','Bearer '||v_key,'Content-Type','application/json'),
    body := jsonb_build_object(
      'from','Studio One Wholesale <noreply@studioonefresno.com>',
      'to',  jsonb_build_array('hairbycatb@gmail.com','studioone.lp@gmail.com'),
      'bcc', jsonb_build_array('justin@webeducationservices.com'),
      'reply_to', jsonb_build_array(v_email),
      'subject', 'New wholesale order — '||v_name||' ($'||v_total||')',
      'html', v_html
    )
  );
end;
$fn$;

create or replace function public.notify_wholesale_order()
returns trigger language plpgsql security definer set search_path=public as $t$
begin
  perform public.send_wholesale_order_email(NEW.id);
  return NEW;
end;
$t$;

drop trigger if exists trg_notify_wholesale_order on public.wholesale_orders;
create trigger trg_notify_wholesale_order
after insert on public.wholesale_orders
for each row execute function public.notify_wholesale_order();

-- These run with definer privilege from the trigger; deny direct calls by clients
revoke execute on function public.send_wholesale_order_email(uuid) from public, anon, authenticated;
revoke execute on function public.notify_wholesale_order() from public, anon, authenticated;
revoke execute on function public.esc(text) from public, anon, authenticated;
