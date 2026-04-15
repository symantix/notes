Hi Sara,

Here's what we've done today:

- For user signup, with added an additional check at the sign-in point, to insure that the user account is setup correctly.  If there is problem with the account, an attempt to resolve it is attempted as the login occurs.  I believe this resolves the issue the we've been experiencing.
- We've added a couple of additional safe-guards to the policy confirmation page, which attempt to address outdated browsers and other possible causes, in order to insure that duplicate emails do not occur.
- We added a check for past quizzes taken by the person who is confirming policies on a recent quiz.  The application will then mark any past (successful) quizzes.  This is another measure to insure that batch email processes don't contact anyone who has recently confirmed their policies.