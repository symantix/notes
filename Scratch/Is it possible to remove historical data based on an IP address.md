Is it possible to remove historical data based on an IP address?  We don't currently have any users setup.  We are applying this command using javascript via the API, whenever an internal IP is detected:

mixpanel.register({"$ignore": true})

But does this also remove historical data attached to this IP?  I found some degree of information on this topic in your help section and other places on the web, but it seemed to be unclear regarding how the ignore command effected historical data, or if there was any other way to remove this data.

Thanks!



I think I've exhausted the available Mixpanel documenation.  It appears that Mixpanel doesn't capture IP addresses, it just uses the IP to geolocate the user, then forgets it.  If we had setup Mixpanel so that each user was captured into a profile from the beginning, it might be relatively simple to delete our data (maybe).  As it is, I have added one more line of code to ensure that our IP addresses are not tracked going forward (pretty sure what I already had was working, but I found another method, so just in case, we can do both), but I don't think there is a way to delete historical data at this point.

I tried to reach out to Mixpanel support, but our plan doesn't include any support except emergency.

I have enabled an option called "identity merge" in the Mixpanel admin.  If we begin defining users in our Mixpanel setup, it will attempt to merge data from the past with new user profiles.  At that point, I should be able to remove entire profiles of data in the admin.

I've asked Jake if he wants to setup user profiles, and I'm waiting on his response.