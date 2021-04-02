# Trade-Bot

This was my first bigger project that I decided to undertake.

At the time, I had been teaching myself to code for about six months or so and wanted to undertake something a bit more daunting. This was during the summer of 2020, where the stock market was in a massive climb, and everyone at my work was obsessively watching it. That inspired me to write this program.

I wanted a project with a database, API requests, and formulas that would have to be implemented to make it work. It all started with wanting a program to send text message updates to my phone with what stocks are, on average, performing the best. Using Alpaca Market's API, I was able to do that. Eventually, the project evolved into a program that actually traded stocks without any human interaction.

This was my first big project, so the code isn't very clean. I debated whether or not I should post this, or if I should clean it all up before posting. Ultimately, I decided not to. It is a good benchmark to show where I have come from and how far I have progressed as a programmer. 

I will, however discuss some things that I would do differently if I were to do it all over again.

1. I would implement a better data structure, one that would dump and store data on a seperate file, or possibly even my home server, so that it could be accessed later. 
2. I would create a better global variables file, or just expand the config file. This would make it easier to change any variables that impact the program, like sleep times between data-reading cycles or frequency of text message alerts.
3. I would make the main function its own page, independent from all other functions used for parsing and analyzing data.
4. I would incorporate more class structures for each stock, so as to avoid multiple arrays and hashmaps/dictionaries.
5. I would implement more webscraping and automation that would find more stock tickers and update which ones should be analyzed.

What I did like about this project is that I learned a lot about optimization. Having only 200 API calls a minute while having 100+ tickers to analyze in each cycle forced me to optimize data analyzations. I remember on the first draft of the program I had an individual API call for each piece of data (price, history, etc.), and eventually it got to the point where my functions would parse through a single dataset provided by a single API call for each individual ticker. I also learned a lot about datasets and API calls, learning how to manipulate them to suit my programs needs.

This is a project that I cringe looking back on because of how messy the code is, but it is also a project that taught me some invaluable lessons that have made me a better programmer.
