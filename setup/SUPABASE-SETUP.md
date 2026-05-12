# Supabase setup -- enabling sign-in + progress tracking

The training site works for everyone with no sign-in. Signing in is **optional** and
unlocks per-user progress tracking (a "Mark as complete" button on each module, a
progress bar on the homepage, and checkmarks in the sidebar).

To enable it, follow the five steps below. Until step 3 is done, the new JavaScript
silently no-ops and the site behaves exactly as it did before.

---

## 1. Create a free Supabase project

1. Go to <https://supabase.com> and sign up (GitHub login is fastest).
2. Click **New project**.
3. Pick an **organization** (default is fine), a **project name**
   (e.g. `mr-bi-training`), and a **region** close to your users.
4. Supabase generates a database password automatically; you can ignore it for
   this use case (RLS handles security, not the password).
5. Wait ~1 minute while the project provisions.

The free tier is generous (50,000 monthly active users, 500 MB Postgres, no credit
card required). You won't hit any limits with this site.

---

## 2. Copy your project URL and anon key

1. In your new Supabase project, open the left-rail menu and go to
   **Settings** -> **API**.
2. You'll see two values you need:
   - **Project URL** -- looks like `https://xxxxxxxxxxxx.supabase.co`
   - **`anon` `public` key** -- a long JWT starting with `eyJ...`
3. Copy both. They are designed to be public -- it's safe to commit them to a
   public repository. Row-level security (set up in step 4) is what protects user
   data, not the secrecy of the anon key.

> Do **not** copy the `service_role` key -- that one is privileged and must stay
> server-side. We only ever use `anon`.

---

## 3. Paste the values into `docs/javascripts/config.js`

Open `docs/javascripts/config.js` in this repo and replace the two placeholder
values:

```js
window.SUPABASE_URL = "https://YOUR_PROJECT_REF.supabase.co";
window.SUPABASE_ANON_KEY = "YOUR_ANON_KEY_HERE";
```

with the values from step 2. Commit and push. Your GitHub Pages deploy will pick
them up on the next build.

> While the placeholders are still in place, the JS detects this and skips
> initialisation -- no broken UI, no console errors.

---

## 4. Create the database table + RLS policies

1. In Supabase, open **SQL Editor** from the left rail.
2. Click **New query**.
3. Open `setup/supabase-schema.sql` from this repo, copy its full contents,
   paste them into the SQL Editor, and click **Run** (bottom-right).
4. You should see "Success. No rows returned." -- that's expected.

What this creates:

- A `public.user_progress` table keyed on `(user_id, module_id)`.
- Row-level security enabled on that table.
- Four policies that together let each user read/insert/update/delete **only
  their own rows**. Other users' progress is invisible to them, even via the
  public anon key.
- An index on `user_id` for fast progress lookups.

---

## 5. (Optional) Enable Google sign-in

Email magic-link sign-in works out of the box. If you'd also like Google sign-in
(recommended -- it's a much smoother UX):

1. In Supabase, go to **Authentication** -> **Providers**.
2. Find **Google** in the list and toggle it **on**.
3. Supabase will ask for a **Client ID** and **Client Secret**. Follow the
   "configure with Google" link on that page -- it walks you through creating
   OAuth credentials in Google Cloud Console (free, ~5 minutes).
4. In the same Supabase page, also add your site URL (e.g.
   `https://movmarcos.github.io/MarketRiskBITraining/`) to the
   **Redirect URLs** list.
5. Save.

After that, both "Continue with Google" and "Email me a magic link" buttons
work in the sign-in chooser.

If you skip this step, only the email magic link button is functional --
clicking the Google button will surface a Supabase error message but won't
break the site.

---

## Done

That's it. Visit the site, click **Sign in to track progress** in the top-right,
choose your preferred method, then mark a module complete. The completion will
persist across devices and across sessions.

You can verify rows are being written by opening **Table Editor** ->
`user_progress` in Supabase.
