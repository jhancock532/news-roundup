# News Roundup

## Brief

Create a crawler that views a series of news websites, summarising the top charity-related stories from the last seven days.

You can then choose to improve the efficiency of the crawler, or expand it to read RSS feeds & our charity client's news pages. Finally, compare your results to OpenAI's agent mode.

## Resources

This `news-roundup` folder contains a basic implementation of a Node based web crawler that uses AI to extract news articles, found in `crawler.js`. 

There's some additional resources related to stretch goals - a prompt for trying out Agent mode in `docs/example-prompt.md` and some information about our client's news pages in `data/torchbox-clients.json`.

## Stretch goals

1. This project's dependencies, Crawlee and OpenAI, both have Python library alternatives. If your team prefers Python, try asking AI to convert `crawler.js` to Python for you.

2. Create a prompt that summarises the top ten most important stories into a single Slack message, with links to source articles.

3. Compare your results to OpenAI's ChatGPT Agent - https://help.openai.com/en/articles/11752874-chatgpt-agent - use the prompt in `docs/example-prompt.md`. This can take 15-25 mins to run, worth doing early!

4. Add cost tracking for input and output tokens used, and try using different OpenAI models - does the quality of the output improve? Is it worth the cost? Can you improve the speed of the crawler by disabling thinking?

5. Improve the crawler so that it reads less irrelevant tokens when doing the initial parse of the news feeds. Remove unrelated classes, elements, attributes etc.

6. Expand the tool to also read content from RSS feeds (e.g. https://www.thirdsector.co.uk/rss/news) 

7. Add a second crawling phase, where an AI reads the news article itself, creating its own summary & relevance rating for staff at Torchbox.

8. Experiment with expanding the tool to read from our client's news feeds and blogs, in case they post something we should get in touch with them about (whether to celebrate or commiserate). An example list of some of our client's news pages can be found in `data/torchbox-clients.json`.

9. Consider how this tool might be hosted to run at weekly intervals & connected with Slack directly.

## Getting started

Copy the contents of `news-roundup` to a new repository, and share this repo with members of your team.

Create a new [OpenAI API key](https://platform.openai.com/api-keys) and share it with the team securely via Bitwarden Send.

Add the API key to your `.env` file, based on `.env.example`.

Change your node version to that in `.node-version` using

```bash
fnm use
```

Install the Node dependencies with

```bash
npm install
```

Finally, do a trial run of the news crawler by running

```bash
npm start
```

You can remove the comments from the `crawler.js` file `CHARITY_NEWS_WEBSITES` array to do a full news roundup.