---
title: "Claude Code + TradingView: Automated Trading"
source: "https://www.youtube.com/watch?v=aDWJ6lLemJU"
author: Lewis Jackson
published: 2026-04-08
created: 2026-04-11
description: "Connect Claude Code to TradingView MCP server and execute trades. Demo: one-shot prompt setup, paper trading mode, safety filters, full trading workflow."
tags:
  - claude-code
  - tradingview
  - trading
  - mcp
  - automation
  - lewis-jackson
---
![](https://www.youtube.com/watch?v=aDWJ6lLemJU)

Chapters  
00:00 Introduction  
01:30 Setup  
05:00 One-shot prompt  
08:00 Paper trading mode  
12:00 Safety filters  
15:00 Full workflow demo
🎵 TikTok: https://tiktok.com/@lewisjacksontiktok  
💼 LinkedIn: https://www.linkedin.com/in/lewisjacksonli/  
📧 The Lewsletter (free weekly breakdown): https://lewisjacksonventures.com/form-pages/lewsletter  
  
  
The last video showed you how to connect Claude Code to TradingView. A quarter of a million people watched it and thousands built the thing with zero coding experience. But it was missing one piece — Claude could read the chart and run your strategy, but it couldn't execute the trade.  
  
This video fixes that.  
  
I'll show you how to position Claude between TradingView and your crypto exchange so it reads live signals, applies a multi-condition safety filter, and places real trades when everything lines up. The whole setup runs on Railway — on the cloud, 24 hours a day, whether your laptop is open or not.  
  
You'll connect to your exchange using API keys, paste a single one-shot prompt from GitHub, and an onboarding agent walks you through every step automatically. It opens the files you need, opens the websites, and waits when it needs something from you.  
Start to finish: about five minutes.  
  
The bot runs in paper trading mode first so you can watch your strategy perform before any real money moves. When you're ready, you switch it live by asking Claude. Every trade — executed or blocked — gets logged to a spreadsheet formatted for your  
accountant.  
  
I'm also including a bonus section: how to scrape transcripts from YouTube channels using the Amplify API so you can extract other traders' strategies and build your own rules file.  
  
Everything here is free and open source. Nothing to buy from me.  
  
⚠️ DISCLAIMER: Nothing in this video constitutes financial, investment, or tax advice. I am not a financial adviser. All content is for educational and entertainment purposes only. Past performance is not indicative of future results. Always do your own  
research and consult a qualified professional before making any financial decisions. Some links above may be affiliate links — I may earn a commission at no extra cost to you.  
  
⏱️ CHAPTERS  
0:00 What the last video was missing  
1:20 How Claude sits between TradingView and your exchange  
3:45 Mac, Windows & Linux — all covered  
5:10 Connecting Claude to your crypto exchange  
8:00 Getting your Bitget API keys (step by step)  
11:30 The one-shot prompt — paste and go  
14:00 Onboarding agent walkthrough  
19:30 Setting up Railway for 24/7 cloud deployment  
23:00 Paper trading mode first — here's why  
26:30 Watching the safety filter block a bad trade  
29:00 Turning on real money trading  
32:00 Bonus: Scrape any YouTuber's trading strategy

## Transcript

### What the last video was missing

**0:00** · In my last video, a quarter of a million of you learned how to connect Claude code into Trading View. And I can tell from the comments that thousands of you ended up building the thing, even if you had no experience. But there was something missing. You could build strategies and visualize them on the chart, even back test your strategies.

**0:18** · Claude could even draw lines on your chart, but it couldn't do the trades.

**0:22** · What you're looking at on screen right now is Claude reading a live Trading View chart, checking a strategy, running a safety filter, and placing real trades on an exchange. And it's even filing those transactions away for your accountant later down the line. By the end of this video, you're going to have five things. Number one, you're going to connect Claude to your exchange so that it can execute trades. Number two, you're going to build a safety layer that's determined by the strategy that you've built. That's so it only trades when all of the criteria line up. Number three, you're going to have the whole thing running in the cloud 24 hours a day and you don't even have to have your laptop open. Number four, you're going to walk away with a system that logs for accounting purposes every single trade and every transaction. It's also going to be optimized exactly for how your accountant will need it when tax time comes. And number five, you're going to have it all in a single prompt that you simply copy and paste into your Claude and it sets up the whole thing in 5 minutes with no experience necessary.

**1:19** · Also, I think it's worth saying I've got nothing to sell you. I don't even want your email. I just want you to make a butt ton of money. Everything here is free and open source. So, right after you subscribe, let's get into it. So, I want to show you how it works. I think most people think that connecting Claude into some kind of AI trading agent is super complicated. You need a developer for it or you need to know code. That's not the case. There are only three tools involved in all of this and they each do one thing. Trading View obviously gives us the price information of the asset.

### How Claude sits between TradingView and your exchange

**1:53** · It shows us the chart. You can also have your strategies housed on Trading View.

**1:57** · If you want to know how to set up your entire strategy, you must watch the previous video to this. Look, a quarter of a million people watch that in about 5 days. If you want to connect your clawed code to Trading View and have a good strategy at the end of it, that's the video to go and watch and then come back here. Now, you can connect your Trading View into your exchange, but the problem with that I found in experimenting in this area is that it gets a bit fiddly and it breaks quite a bit. So, we're actually not going to do that for this. Instead, we're going to put Claude right in the middle between Trading View and the exchange. Claude is going to watch all of the signals that are taking place on the screen on the trading view. Claude is also the one that has the context of the strategy. If any changes would ever need to be made to the strategy, Claude would be doing that and interacting with Trading View to do it. Now, when the data all lines up from the Trading View side, Claude is watching that and then Claude can go to the exchange to actually execute the trade. Obviously, when that trade is executed or even if it's not executed, it's reporting all of that information within Claude's structure in your computer. So whether it needs to log a trade that's taken place for accounting, it's going to go and do that. If a trigger fires because of all the conditions being met, then it's going to log that information somewhere else. And if a trade doesn't trigger because the condition didn't meet up, then it will also log that information, too. And you can access that information anytime you feel like it, just by interacting with Claude. So, Trading View and the Exchange actually never talk. They go through that central brain which is Claude. For this entire setup, I'm using a Mac, but I saw in the comments of the last video that many of you are using Windows and Linux. Now, while I think going through this whole process and this whole video is useful for you, your entire setup tutorial is actually in the GitHub specifically for your machine.

**3:43** · And while I am using a specific Exchange, which we'll get to in a second, I've listed the top 10 exchanges that you can use in this system. Each one has its own individual tutorial for the setup element. You've got no excuse.

### Mac, Windows & Linux — all covered

**3:56** · One more thing before we set this up.

**3:58** · I'm also using Whisper Flow throughout this demo. I've been using Whisper Flow for about 12 months. I've spoken almost a million words into this thing. And essentially, instead of typing, I'm just transcribing by a simple click of a button on my keyboard. I found I get the best results from my AI when I'm using this transcription tool and talking freely and naturally to Claude. If you're interested in using it, you can set that up along the way. First things first, we want to connect Claude to our exchange. This will allow us to do the trades when Claude determines that it's time. Obviously, the exchange is where your money lives and where the trades are going to be executed. All we need to do is give Claude the permission to talk to the exchange. I think a lot of people think connecting to an exchange is going to be this complex developer type of thing. It's not scary at all. I'm going to show you it very simply. And in this connection, we're going to extract three pieces of information. One is the API key, the other is the secret key, and the other one is a passphrase. If you think of them all as keys, all three have to come together to open the door.

**4:56** · And when you open that door, you've essentially given Claude access to be able to execute these trades for you.

**5:02** · Now, personally, and for the purposes of this video, I'm going to be using an exchange called BitGet. Bitgate have been very kind and have offered $1,000 of bonus money when you deposit into BitGet. And that's really cool cuz you can use that money to actively trade for you by the bot that we're setting up here. Of course, this will work with any exchange that has an API, but Bit's really the only one offering you $1,000.

### Connecting Claude to your crypto exchange

**5:25** · So, bit of a no-brainer. That's also going to be the exact tutorial that I give on this video. The link for BitGet is in the description, but you don't have to click it just yet. Let's go through the process, and you'll see something really cool that happens along the way. So, of course, you're going to have to download the BitGet app, but it looks just like this. So once you've downloaded it, let's click into it.

**5:43** · You'll see here at the bottom left hand side there is a home button. We're going to click the home button. Then on the top left there's a profile picture.

**5:50** · We're going to click that profile picture. Come all the way down to the bottom where it says more services.

**5:55** · We're going to click more services. Now we want to look for tools. So as you can see on the top kind of menu thing, we've got popular rewards earn trading assets.

**6:03** · Then we've also got tools. So we're going to click tools. And right there you'll see API keys. So, we're going to click API keys. We now want to create a new API key. We're going to click that button. We're going to go to automatically generated API keys. And right here, you're going to have a few ways to name this thing. So, we want to call this bot something. Let's just call it trader thing. Your passphrase is going to be your password, right? So, you want to keep this very personal to you. I'm just going to call it password 1 2 3. For the bind IP address, you don't need to put that in. But what I will say is that we want read and write only permissions. So you can select as many as little as you want. This is completely up to you. But I'm going to select futures, open interest, spot trading, spot margin, copy trading, and taxation and sub accounts. I'm going to leave crypto loans uh P2P and transfer.

**6:59** · I'm going to click confirm and it will now give me uh I have to go through this whole verification process. So let me go and do that. And now I've done that. I now have my API key and my secret key.

**7:10** · And all we want to do now is put these in our environment file. Okay. So now you've got your API key. You've got your secret key and your passphrase. This is really actually really important information. What I want you to do is copy and paste that somewhere that is safe on your computer just for now.

**7:25** · We're going to keep that to the side and very soon we're going to use that information and just plug it into clawed code. Now the bit you've been waiting for, the oneshot prompt. This prompt is I love making these prompts because essentially what I've created here is an onboarding agent for you and I think I'm going to do that for all of my tutorials moving forward. It's so helpful. It removes all the complexity. You don't need to follow these different commands that you put in your terminal. It does the whole thing for you. And you'll see along the way here, it's just super helpful. It allows you to get the whole thing done in about five minutes. And we're going to go through it right now.

**7:56** · Because normally stuff like this is like cloning a repository, editing configuration files. It's like sounds like gobbledegook. And if it sounds like gobbledegook to you, it's because it's unnecessarily complicated. And now that we've got AI and specifically with this onboarding agent in the prompt, we don't need any of that complexity. Plays no importance to us. It just does the complex stuff in the background where we just type one key at a time. It's super easy. So this single prompt will turn Claude into an onboarding agent for you.

### Getting your Bitget API keys (step by step)

**8:25** · It will stop when it needs something from you. It'll wait for you to do it.

**8:29** · And when you've done it, it will move on to the next stage. It'll even open files and websites for you so that you're not going around your computer trying to find them. So, using the top link in the description of this video, you're going to come over to GitHub. GitHub looks like this. Okay, I know it looks a bit complicated. It's seriously not. We're going to click exactly where we need to click on here. No extra steps. Don't worry about this whole thing at the top.

**8:51** · Of course, the video that you need to watch as a prerequisite before this is right here. you can just simply click this video and get taken over to the video uh where we set up this bot and the strategy and everything. So, um look at that. 270,000 people watch that video. Incredible. Okay, so as you come down, all you need to do is come down to this oneshot prompt section right here.

**9:12** · You can see that there are a series of steps that we will go through as part of that onboarding experience. But again, you're not having to do this individually. It's just going to take you through the process. and it does it in such a way where it's it's kind of amazing.

**9:26** · Right, let's get into it. So, the oneshot prompt, this is the thing that you need to paste. So, you're just going to click that link to the oneshot prompt uh page. You can just come up to the top right, just click copy raw file. That's completely fine. Then, you're going to come over to your um terminal.

**9:43** · Obviously, we want to open up in Claude.

**9:46** · Now, what I do, I don't advise you do this. You can do this only at your own risk is I like to do something called dangerously skip permissions. It says dangerously for a reason. So I'm not advising you do it. You can just type claude and click enter and then you're in claude already. Or you can do kind of dash dangerously skip-permissions.

**10:07** · Basically what this does is it sets up claude with auto approval on so I don't have to keep kind of approving things as we go. So I'm going to click okay. Yes, I trust it. I've done that too many times. Probably too many times to be honest. Okay, so now we're in Claude. We have copied the oneshot prompt from over here. And look, there you go. It's done.

**10:27** · Now we're just going to let the onboarding agent do its its thing. We're going to read the feedback that it gives us because it's going to go through, you know, everything in in nice detail. I'm going to make that nice and big so you can see it on the screen here. Okay. So, before we start, one thing in this video, Lewis is uh talking to Claude rather than typing it. I mentioned Whisper Flow earlier. So, I love this because, you know, if you want to use Whisper Flow, then you can just say, "Yeah, I want to use Whisper Flow." So, you say yes. And what's really cool about this is that it will actually take you to Whisper Flow. The onboarding agent does the thing for you, right?

**11:00** · It's just opened up Whisper Flow for me and you get your first month for free.

**11:04** · It's just opened it up for you. Didn't even need to go to type in Whisper Flow.

**11:08** · Anyway, Whisper Flow is really cool.

**11:09** · Obviously, I love the thing. Um, I've said yes and it says, "Type done when ready." So, I'm just going to type done to move on to the next stage. Anyway, we're just going to let this go through its process. It's cloning at this stage the GitHub repository. And that is basically cloning the whole process that I've created. It's now installed that into your computer. Now, step two has come up because now we need to choose your exchange and get your API key, which we did earlier in the video, of course. Um, it's asking you now which exchange are you going to be using cuz in the video I'm using BitGet. If you want to use the same, you can just type bitget or you can type any exchange that you use. If I wanted to type Binance, it would then give me the tutorial for Binance to set the API key up. But because we're using BitGet, you can type number one or just type BitGet and uh click enter. Again, what's really really cool here is it will then open up BitGet for you so that you can make your account or sign in. It's it's truly just done for you. I I love this so much.

### The one-shot prompt — paste and go

**12:08** · Okay. So, uh I've already got an account with BitGet. Of course, I'm going to type done because I've already got an account and we'll wait for step three to take place. So, it said, "Let's get your API key." Here's the exact process for doing that. We've obviously gone through that in the video already, but if you wanted to follow a 13step process, click by click, you can absolutely do that here. Um, now we've got our API and our secret key and our passphrase. So, I'm going to type ready as it asked me to because I have those uh documents. Now you're about to see something really good because in my whole journey of learning how to code and do this AI coding stuff, there was one thing that was the bane of my existence and that was called env files, environment files.

**12:50** · These env files don't show up in your computer when you go to the folders.

**12:53** · It's deeply frustrating um because they're secret information. Like you don't want the information in an environment file to be shared and so it needs to keep it secret from people. So I would always have to end up asking it, can you please open the env file? so I can edit it. Well, as you know from this onboarding process, you don't have to do all of that stuff because it opens it for you. In fact, it's just opened it on my other screen. I'm going to bring it over to you here so you can see it. And let's bring it over. Here we go. It's just opened the ENV file for me so I don't have to go and find this confusing file. Anyway, so in here we've got our Bit API key that we simply enter right in here. We've got our secret key that we enter in right here. remember to do it after the equals sign. Then we've got our passphrase that we already created and obviously we've got that URL which you don't need to change. Um there's a few other things in here that you can go ahead and change if you want to be a little bit more proactive and that is the amount of money that you're going to actually be allowing this agent to trade. So for example, if we've got $1,000 and that's all we want it to have access to, we're going to put a,000 into here. Uh it's just the portfolio value.

### Onboarding agent walkthrough

**14:00** · This is the amount that we're going to be trading. We're going to say $1,000.

**14:04** · There's also a few other limits in here that you can enter. So, what is the single largest size of trade that you want to do in any given trade? We've set this to $100. And the maximum amount of trades per day that we want it to make.

**14:17** · Let's say it's three. It could be 100, 200, a,000, I don't know, whatever you want it to be. And then also the chart that we want to look at. I wouldn't even necessarily edit this because you can actually just talk to Claude and get it to change this. You can do that. You can talk to Claude for any of this and tell it to change it. and the time frame that we're looking at. Obviously, right now we are set to true to run in paper trading mode. There's a reason for that which we'll get to later. Okay, so we've now put our API key and our secret key and our passphrase in here. I'm not going to do it for the video cuz I can get hacked if I do that and everyone can see. So, I'm going to leave that clear for outside of the tutorial. But, let's say that I've actually done that now.

**14:55** · When I have done that, I'm going to click done and it's going through the guardrails questions now that we I talked about earlier. So, question number one, how much of your portfolio are you going to be working with in US dollars? Let's just say it's $500. I just want to show you how it edits the ENV file as we talk to it. So, I've put 500 into here. Question number two, what's the maximum single size of any trade? I'm going to put 99 just cuz that's memorable. It's going to ask me one more question. How many trades maximum should the bot place per day?

**15:24** · We're going to say 67 for my millennials out there. Okay, so we've told it these things and now it's going to go to the ENV file. It's saying now writing settings into your ENV file. I'm going to ask it now just to open the ENV file again so I can see that it's made the changes. Can you show me the changes that you've made in the ENV file by opening the ENV file, please? Okay, so I've just asked it to do that. It should just open it. Yeah, it opened it up in a different uh window here. And there we go. We can see that the portfolio value is now 500, the $99 maximum trade size and the 67 maximum amount of uh trades per day, right? So, it can update all of this stuff just by talking to it is the point. Okay, so it's done all of that, but we were on step three, which is connecting to Trade View. Obviously, if you haven't done the connection to Trade View and their MPC, you want to go to the previous video to set that up because you're going to need that for this. But conveniently, there's the link for the video to go and have a look. So, how cool is that? So, if you've already set that up, it will run a health check now. And you just type in connected. So, I'm going to say connected, and it's just going to check that the trading view is in fact connected. If it is, then it will proceed to the next step.

**16:34** · There it is. It says trading view is connected and live. We're on the Bitcoin USDT chart on the 15minute chart. Now, it's asking me to build my strategy. On the previous video, we already created a strategy. But since the last video, I kind of created a new one just to show more frequent trading on on this video.

**16:51** · If you want to build your custom strategy, you can just type yes and do that. Now, you can type skip just to use the example that we're using in this video. Or you can make your own strategy and and tell it your own strategy. In my case, I've already built a strategy for this and I want it to retrieve that strategy from my computer. So, I'm going to tell it, hey, so I created a strategy for this. It was like a scalping strategy. Could you implement that?

**17:14** · Remember, talk naturally to to the AI, please. It's just you don't need to be I I I know I asked my mom and dad to talk to chat GPT and they they they put on their phone voice. It's like, "Hello, I would like to know." It's like you don't have to do that. You just just talk to it like it's a human. Okay. Sorry, Mom and Dad. I I just I had to out you there. Um so, it said, "Tell me the details of your scalping strategy." Um well, I I already made it. It's somewhere in the computer. Can you please go and find it? I get frustrated sometimes when it's not reading my mind, but it will it will do that soon. And for those of you that don't know already, we actually created something called a rules.json file, which is basically a whole kind of text document of the entire strategy.

**17:54** · All the intricacies, all the conditions that need to be met in order to execute a trade, all the different indicators that would need to be used, the pine script for the for the indicator that goes as part of the strategy on Trading View, it's all kind of in there. And a lot of the process that follows that is from the rules.json file. So it says your strategy is in. Here's what your bot will check before every trade. So this is the criteria. It will only buy when all three of these are true. The price is above the VWAP. The price is above the EMA, the 8 EMA in an uptrend.

**18:25** · That's to confirm an uptrend. And the RSI um has to drop below 30 to do that.

**18:30** · And it will sell when all of these signals are true. and it's going to do it on the XRP chart on the one minute time frame with a 0.3% stop- loss from the entry. That's the strategy. By the way, when I created that strategy, I I pulled it out of my butt. Okay? Don't follow this strategy. This is not going to be a winning strategy at all. You have to apply apply your own strategy or go and get a strategy from someone else.

**18:52** · Okay? There is actually a very simple process for going out to get transcripts from a YouTuber that you watch and try to deduce and determine what their strategy is from the transcripts of their videos. I'm going to attach that to the end of this video. If you think the video is over, it's not. Keep watching for that remaining pit. You can also look in the chapters under this video here and just go straight there if you want to kind of scrape someone else's strategy from their YouTube channel. Now, step number five is that we're going to deploy this to railway.

**19:23** · Railway is going to allow us to have this on the cloud. So, it's running 24/7. Whether your computers on or off, the whole strategy is going to work.

### Setting up Railway for 24/7 cloud deployment

**19:31** · Trades can be executed in your sleep.

**19:33** · So, railway is how we're going to do that. We have already set up railway in the previous video. So, it says the railway CLI is installed, but I'm not logged in. So, I can just run uh a specific code in my terminal, and all I do is copy that. Um, I can come up to a new window and just type that. What it should do is ask me if I want to open my browser up to login. I'm going to click yes and click enter. And it takes me over to railway to login. So, it's it's a success. I've just logged in and I can close that out. And now I can see I'm logged in. I'm going to close that window. And I'm just going to tell it done because it said come back and type done. So, that's what I'm going to do.

**20:12** · Super simple. I hope you can see how this isn't complicated at all to do. Uh, now how often do you want the bot to check for trades? This is completely up to you. You can describe what you want with your voice, which is, you know, I'm just going to say every 4 hours on here.

**20:25** · So, I'm just going to type number one.

**20:26** · But, as I said, rightly so, the strategy is running on a 1 minute candles. So, I might want something more frequent. Just know I think that when you make something so frequent, you can start to get um obviously you're using the AI a lot more, so you might get charged for that. But anyway, regardless, I've put in every four hours. it doesn't matter for the demo. And it's just going to install that into railway. And it's doing something called a chron job, which essentially chronologically there's like a a task that happens every so often, whether that's every 4 hours, it will just run that task. Now, I can see here that it's actually not got an env file for railway. And so it said, now it's actually caught me cuz I haven't done this yet, but the bitget get API key isn't in and the the secret key isn't in and the passphrase isn't in yet. So, it's just alerting me that the ENV file doesn't actually have the information in. So, it's thinking. It knows what it's supposed to be doing. I just haven't done my part yet. So, I'm going to do that now off camera and uh we'll get back to this. Okay. I've done that now. So, I'm going to click done.

**21:25** · Uh how is Claude doing? Good. Thank you, Claude. Okay. So, let's move on to the next stage. We'll just see what happens.

**21:31** · Okay. So, it's done a whole bunch of things here in the background. I changed a few things just to suit the amount of money that was actually in my account.

**21:37** · So the portfolio we're going to say is just $100 that we're going to use. The maximum trade side is five and we're just going to set it to a,000 trades a day if it can. It's all on railray right now and it's on paper trading mode which is really important for this first stage. Um step six happened. It just added my trade log. So this is that that spreadsheet that's going to log all of the trades and the outcomes of all of those at tax time. That's going to be really useful for you. It's going to save you thousands of dollars. Um, if you want to just access that file at any time, you can just ask Claude to open up your trades log for accounting and it will just do it. Okay, so very easy. Um, there's nothing in that right now for me, so uh, we'll do that later. Step seven then came across and it said what your bot is going to check before every trade. Obviously, we know what it's going to do for a buy, what it's going to do for a sell. If any single one fails, do not trade. um and it'll tell you which one failed and the actual value that it saw. Number step number eight is to actually just watch this thing run. Right? So, it actually went out and did a run. It it tried to do a trade based on the conditions that we have. All on paper trading, by the way.

**22:44** · It showed us the variety of indicators that we're using for the strategy being price, VWAP, EMA, and RSI. Told me the value of all of these things that took place. And then it did the safety check that we talked about, and it blocked the trade. And that was because the price is above the VWAP, which we want. The price is above the EMA, which we want. The price is within 1.5% of the VWAP, which we want. But the RSI was 38.26, and it needs to be below 30 for a buy signal.

### Paper trading mode first — here's why

**23:11** · No trade fired, and that was exactly right. The the bias for this trade has been very bullish, but the conditions haven't pulled back enough to to make it to make it ready to do a trade. So, um, in fact, what I can see has happened here is actually it did open up my trades document just to show me that it failed. So, I'm going to pull that up here. Uh, let's put that down here. You can see right here at this time, very specifically, BitGet uh, on this chart blocked the trade for these reasons. And this is where, you know, this is the the trades document that you're going to be using to send to your accountant, right?

**23:45** · It's going to when it does actually create the trade, it's going to fill out all this information and it's everything you need to know including a note like it failed because of this reason. And there's also a secret note there if you're interested to read. All right, so that's it. The bot is completely live.

**24:00** · It's going to run every 4 hours on railway or whatever you've determined on your side. It's currently in paper trading mode. All you have to do to change that is tell it, can we do it with real money now? And then it will just go and do it. Now, before we do a full demo of this to show you it working, I want to make sure that you hear what I'm about to say. Nothing in here is financial advice. I know. Oh, it's not not financial advice. It's not.

**24:23** · This strategy that I created here is pulled out of my butt. I pulled it out of thin air. I don't know what it's going to do. It's probably a bad strategy. You need your own strategy for this agent. If you make a good strategy, the agent will execute it well. If you make a bad strategy, the agent will execute it well. Okay? it will do whatever you've done. And so if it's good, it will end up good. If it's bad, it'll end up bad. So this is why I want you to start in paper trading mode.

**24:47** · Watch it do a whole load of pretend trades. And then when you're comfortable and you've back tested your strategy and you've done it for a few days at least, you can see the performance of it. Then start to turn the real money on. If you want to turn the real money on, all you have to do is go to Claude and say, "I want to make it with real real money trading now." And it'll just do it. All right. So what you can see right here is it's doing the trades right now. It's reading the chart. It's applying it through that filtration system of the strategy. It's looking at the conditions and lining up the conditions. If the conditions are met, it will actually approve the trade. And you can see that with the green check marks. And if the conditions don't line up, then it just blocks the trade and it doesn't take place. So you can see this is actively trading for me in the background here.

**25:31** · And this will continue 24 hours a day all the way up to the limit that I have set for the maximum amount of trades that I've done. And all of it is being saved directly to a spreadsheet. And this is what you have just built going through this video. If you're watching this on your phone, you're not going to get the full experience here. You're not going to be able to build it very well.

**25:49** · Save this video and come back to it on your computer. The oneshot prompt is in the first line in the description of this video. One paste and you're done.

**25:58** · All right, go and make some money. See you in the next one.

**26:07** · Now, as promised, I'm going to teach you how to scrape the transcripts of YouTube channels that you kind of listen to, uh, because you think that maybe their strategy is going to be superior to yours. Not saying it will be, but if you want to know how to do it, this is how you do it. There's a link in the description of this video. The onboarding agent should actually also prompt you to to explore this idea if you want to as well. Um, you want to come to Appify. The the links will be everywhere. There's even a link in the GitHub. All you have to do is come over to console and then on the left hand side you're going to see a search button. We're then just going to type in API and you're going to find the button that says API tokens. Click API tokens.

### Watching the safety filter block a bad trade

**26:44** · On the right hand side, you'll see create a new token. You can just click create a new token. Um, it will show you, you know, here's a description uh trading bot thing. And then you click create. What it will do then is create you an API token. All you have to do is click the copy button on your API token.

**27:03** · All you have to do is come over to Claude and basically just tell it, "Hey, I've got my API key for Appy. Can you please open up the ENV file so I can put the Appify API key in there?" We'll click enter on that. And what it should do is essentially just open up my ENV file to put all of this in. We'll wait for the ENV file to be created. And when it opens it, it's just the same process as we used before. Just copy your API key, come over to your ENV file, there should be a location for you to paste it, and there you go. You just paste it in. Uh, click command save or just save that document. And then you're done with that connection. What you want to do at that point is then come over to YouTube and find the content creator that you're most kind of looking at here. Let's say it's Blockchain Backer. You could click his channel, take his URL for his channel, then come over to your Claude and just say this.

**27:56** · Hey, I want you to scrape the transcripts of the last 100 videos from Blockchain Backer. I want you to use Appify to do it. You can look in the env file for my Ampify API and yeah, scrape all the data and then put all the transcripts uh into a very easy to find document and make sure that you've kind of understood everything from the transcripts because I want to create a trading strategy based on what what you can deduce from the transcripts of blockchain backer. So I want to create a trading strategy that is reflects what blockchain backer is doing. Okay. So that's what I've just spoken to it. I'll paste in the the URL for blockchain backup. I'll click enter. And that can be any YouTuber, right, that you want to kind of deduce their strategy from. And it will go out. It will link up to Appy and then ultimately even create that full strategy for you to put into your rules.json file. You can see here I I didn't actually paste in my Appify key, but it will do it all for you. It go through the whole process. It might take about 10 20 minutes, uh, but it will do it all. All right, thanks for watching this video. I'll see you in the next one.