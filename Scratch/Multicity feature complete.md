Multicity feature complete

Discoveries made:
- Changing a question's type compromises the ability to get the past answers to the question.  The API still contains those answers, but Typeform warns against doing this, and the answers are gone in the admin.
- As a results, we created two scripts that will need to be run on the live application before we take everything else live.
	- One script caches all quiz results to the quiz_connections collection of the application database
	- One script deletes any pre-existing connections to quiz's that have now been deleted.
	- This protects us from the risk of lost data in Typeform's hands, and paves the way toward referencing our own database for everything except a new quiz