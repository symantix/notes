Deploying Nickel to Netlify

Moving all api calls to serverless function calls in
	[schools].js
	schoolDetail.js
	schoolNoData.js
	Layout.js
	
Tried to resolve error in _documents.jsx, around lines 13-16, but couldn't find a solution.  Strangely, deleting this file allowed the application to compile.  And it's working, but with a 404 when you try to go to the school page.  I don't know if the missing documents file is the cause, but it still works perfectly locally.  Jesus said that it still works because it has already compiled the styles, and he's looking for a way to make the file work with Netlify.