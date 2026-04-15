This is fixed.  The issue was that Firefox for android is not sending the origin header, which was breaking the live-site tests.  I have set the origin to default to 'schoolahoop.org'.  Since this is a fringe case, we can safely assume that most requests from this browser are live.

It took hours to trace this down, because Firefox for android has no console or developer tools.  Here's what I did:

- Created ad-hoc console by assigning console logs to vue data property (screenshot attached)
- Attempted to replicate exact Android setup locally.  Succeeded in replicating issue locally, which eliminated the  possibility of this being caused by a Lambdatest quirk.
- Traced functionality little by little, compiling over and over again for each little trace step, to find the fail point.  This is so that each trace step could be tested remotely in Lambdatest.