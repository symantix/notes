Spam issues

- We may have already fixed this problem last week, when I fixed the unsubscribe links, which weren't working (no link info).  Missing or broken subscribe links are listed as one of the causes for spam filtering.
- We can upgrade Sendgrid to a $60/mo plan.  This will give us a dedicated IP.  We currently use a shared IP, so our email reputation is shared with whoever else uses that IP.  The current spam flags that we are seeing in Sendgrid indicate that this may very well be caused by an IP address that has a bad reputation.
- We need to add some lines to their DNS, which will help to verify that we have permission from the domain owner to send from the IP address that we use.