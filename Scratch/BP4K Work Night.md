BP4K Work Night

Hi Ian.  Here's the latest on BP4K.

While working on the print styles, I discovered a condition in which the quiz loading mechanisms were looping in the background.  This appeared to have no effect on the user experience, but could definitely be causing bugs that may seem unrelated.  Investigation into this lead to a few hours of tracing the loading process as I navigated through the site, and re-organizing the loading logic.  This meticulous code review lead to the discovery of a couple of other bugs, which are now fixed.  By the time I was done, the scroll bug had also been fixed as a side effect of cleaning up the code.  

I also believe that this cleanup resolved any remaining problems with connecting new and orphan quizzes to users, and tests confirm this probability.  However, this issue should still be monitored, and as before, current orphans won't be re-attached until the user takes another quiz.

There were many frustrating moments today.  However, it's worth remembering that this was my first project using Mithril, first using Node.js, and first using Fauna.  The learning curve was massive, but I believe that today's labor has added a great deal of stability and consistency to the overall user experience.  It was also a fruitful learning experience.  And though I'm definitely ready to crash, it feels like a day well spent.

The one thing I haven't completed yet, however, is the print style task that I began with.  My apologies, I was determined to wipe the list clean today.  I will aim to complete it tomorrow.  

A couple of questions:

1:  Should the print styles 1) only fix any major issues and make sure everything is readable, 2) look neat, but not necessarily pretty, 3) look neat and pretty, or 4) look as close to the website as possible?

2:  Do you want me to record all/some/none of the time I spent debugging today?  Now that I'm salaried, I wonder if the considerations are a bit different.