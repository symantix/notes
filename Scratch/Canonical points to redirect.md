## Page has only one dofollow incoming internal link
This pertains mostly to the login pages, and one blog post.  This is saying that we only have one internal link pointing to these pages.  Unless you want to add some links somewhere, I think this is fine.

## Orphan page (has no incoming internal links)

## Redirect chain
This pertains to only one link, the home page, and it is only a hypothetical.  Redirects are necessary for when someone enters our site from a URL that doesn't match our standards, such as non-secure URLs, or URLs without trailing slashes.  As long as we don't publish invalid URLs ourselves, then the only time this would happen is when someone entered an invalid URL manually into their browser.  We can't prevent this.  In the case of the redirect chaining, this is from a non-secure www domain, to a secure www domain, and then to a secure non-www domain.  This is  how Netlify's own redirect to our primary domain is setup to redirect, and the only way to bypass it is to disable Netlify's redirect policy, and implement our own, which skips the middle step. But this would only address fringe cases as described above. I recommend we leave this as-is.

## 3XX redirect
See above.  This error is caused by 75% of the same circumstances described above.  There are 4 errors here, and none of them have internal links, which means we have no control over them.  As above, these redirect's would only occur with manual URL entry.

## HTTP to HTTPS redirect
Same as above.  A few redirect policies are good and necessary.

## H1 tag missing or empty
This pertains to the signup, login, and profile pages only.  Unless you want to add a header to these pages, I don't think it's necessary to fix this.

## Multiple H1 tags
This pertains to the quiz, which has a header at the top of each step.  We could change these to h2 tags, which would resolve this error, but would cause another error for having no h1 tag.  We don't need to do anything here.

## Slow page
I have reduced the size of numerous images that either hadn't been compressed before, or could still be compressed significantly more.  This, together will all of the great work that Jarrod did to reduce our javascript payload, has resolved the issue.