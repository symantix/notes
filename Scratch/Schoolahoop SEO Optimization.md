Schoolahoop SEO Optimization

- Examined all installed modules in order to eliminate deprecated code
	- Uninstalled mailboxlayer, no longer used
	- Uninstalled auth0, we only use the auth0-js module
	- Moved eslint module to development mode only, so that it is not installed on the live application or staging environments
	- Uninstalled validate.js, only used in one place on the site, and it doesn't appear to do anything significant
	- The only way to reduce javascript any further is to start extracting code from installed modules, so that we can remove unused code by uninstalling those modules.  This will be very meticulous and time-consuming, and perhaps impossible if the code is compressed.
- Attempted some conditional loading of quiz components.  Although it works, I'm not sure it's having any significant impact.
- Removed extra h1 tags from blog posts, changed to h2
- Switched nuxt.config.js target value to "server"
- Used webpagetest.org to find places for improvement
- Installed nuxt-helmet, which takes care of several security headers that need to be in place, like X-Content-Type-Options, Strict-Transport-Security, and others
	- This ended up not working correctly.  I tried several different approaches to this, including adding them to the netlify.toml file, as well as the nuxt.config.js file.  The headers showed up in my local environment at best, but never in staging or live.  It's probably worth spending more time on this particular change.

All of this effort moved the mobile page speed score from 54 to 58.  All major issues were resolved on Ahrefs, with the exception of a single redirect chain, which Netlify imposes with their own redirect rules (secondary domain redirected to primary), and I have never been able to find a way to change it.

These changes had to be carefully merged into the live site for proper testing, since there is penalty for subdomains under some inspection tools.  Here are some PRs to keep the pipeline is in sync:

Staging: https://github.com/lincolnlabs/schoolahoop/pull/1077
Staging2: https://github.com/lincolnlabs/schoolahoop/pull/1078