---
title: "How To Create A Personal Zero Human Trading Firm"
source: "https://www.youtube.com/watch?v=T6jdfZ317Vw"
author:
  - "[[Lewis Jackson]]"
published: 2026-04-18
created: 2026-04-18
description: "Interview + live walkthrough of PaperClip (agent orchestration framework) showing how to structure an AI ‘trading firm’ org chart: research/backtesting agents, risk layer, reporting, and execution concepts."
tags:
  - ai-agents
  - agent-orchestration
  - trading-systems
  - workflow
---

> NOTE: Promotional links and CTAs from the original YouTube description were removed during ingestion cleanup.
![](https://www.youtube.com/watch?v=T6jdfZ317Vw)

▸ Work with me 1:1 to build your AI system → https://www.workwithlewis.com/ai  
  
Build a Zero-Human AI Trading Firm With This Free Tool  
  
🔗 Links from this video:  
▸ Watch my live £50K → £500K trades in real time:  
https://10x-app-production.up.railway.app/dca  
  
▸ My free weekly breakdown of what matters in markets:  
https://lewisjacksonventures.com/form-pages/lewsletter  
  
🎙️ Find dotta online:  
▸ X/Twitter:  
https://x.com/dotta  
  
📱 Follow me:  
🎥 YouTube:  
https://www.youtube.com/@LewisWJackson  
🐦 X/Twitter:  
https://x.com/WhatSayLew  
📸 Instagram:  
https://www.instagram.com/lewis.w.jackson  
🎵 TikTok:  
https://tiktok.com/@lewisjacksontiktok  
💼 LinkedIn:  
https://www.linkedin.com/in/lewisjacksonli/  
📧 The Lewsletter (free weekly breakdown):  
https://lewisjacksonventures.com/form-pages/lewsletter  
🌐 Website:  
https://lewisjacksonventures.com  
  
AI trading agents can now research ideas, backtest strategies, manage risk, and execute trades completely autonomously — and the framework to build them is free and open source.  
  
I sat down with dotta, the anonymous founder of PaperClip, an AI agent orchestration framework that just crossed 50,000 stars on GitHub. In this conversation, he walks me through a live screen share showing exactly how to architect a zero-human AI trading firm from scratch.  
  
We cover what PaperClip actually is and how it works as an orchestration layer for AI agent teams. dotta explains the shift in thinking from using a single AI agent to building structured teams of agents — each with specific roles, skills, and accountability — organised under an org chart with a CEO agent you direct as the board.  
  
He shows how you can bring your own agents — whether that's Claude Code, Codex, Gemini, or any open source model — and plug them into one coordinated organisation.  
  
The practical walkthrough goes deep. We build out a research team for generating and backtesting trading ideas, discuss how to set up risk management agents, and explore how these teams communicate and report back to you.  
  
dotta shares how he personally uses PaperClip to run his own projects and what he's learned about giving agents clear instructions, injecting your own taste, and treating them like real employees who need attention and guidance.  
  
If you want to scale your trading operation using AI without writing everything from scratch, this is the episode to watch.  
  
⚠️ DISCLAIMER:  
Nothing in this video constitutes financial, investment, or tax advice. I am not a financial adviser. All content is for educational and entertainment purposes only. Past performance is not indicative of future results. Always do your own research and consult a qualified professional before making any financial decisions.  
  
Some links above may be affiliate links — I may earn a commission at no extra cost to you.  
  
⏱️ CHAPTERS  
0:00 AI Is Already Trading For People  
0:32 What You'll Learn Today  
1:45 What Is PaperClip?  
2:51 Org Charts and Agent Teams  
5:13 Marketing Video Demo  
8:39 Why Orchestration Beats Solo Agents  
15:22 Research and Reporting Agents  
18:51 Onboarding and Setup Walkthrough  
22:21 Building a Backtesting Ideas Team  
26:09 Adding a Risk Management Layer  
29:45 Giving Agents Clear Instructions  
37:00 Real Results and Lessons Learned  
42:13 Treating AI Agents Like Employees  
47:13 The Future of AI Agent Teams

## Transcript

### AI Is Already Trading For People

**0:00** · Right now, while you're trading, reading charts, and analyzing news, other people are using AI to do that whole thing completely autonomously, 24 hours a day.

**0:09** · They don't take a salary, and they have no days off. And that's not some outrageous future that we're thinking of. That's happening right now. Guest today is Dota. He is the founder of Paperclip. It's an open-source AI agent framework which just crossed 50,000 stars on GitHub. And if you don't know GitHub, that's a lot of attention. but he is anonymous by choice which you'll see in this interview today. He's going to show you live on screen how to create a zerohuman AI trading firm. By the end of this video, you're going to know what Paperclip is and how it works.

### What You'll Learn Today

**0:39** · You're going to know how to transition your thinking from single AI agents into teams of agents. And you're going to see the full architecture of a zerohuman trading firm. one that can research ideas, back test strategies, manage risks, and even execute trades while you're not there. So, if you've ever wanted to expand your trading efforts, this is free. It's completely open- source, and by the end of this video, you're going to be able to build it yourself. Okay, Dota, what you going to break down for us today? All right.

**1:10** · So, we are going to look at Paperclip, which is a AI agent orchestration software uh that's put together by me and our team that will show you how you can uh basically create we're calling it uh zero human companies. Though, I I guess I'll even start right out of the gate and say I find that uh AI agents are actually best suited for companies where uh humans are kind of guiding them and shaping them. So maybe think of this more as like an AI team.

**1:40** · So yeah, paperclipip is a tool that you can use to build an AI team for really any part of your business. And an important part about paperclipip is it gives you kind of um accountability for these AI agents and the ability to sort of inject your taste and shape them and guide them and organize their work um in a way that I don't really think exists in kind of any other software. It's free and open source and so yeah, I think we can use it to to build out some some assistance for our trading.

### What Is PaperClip?

**2:09** · Okay. So, for my audience here, when they finish this video, what are they going to leave with?

**2:14** · So, first thing you're going to know is uh like what Paperclip is and how to actually use it. Um the second thing would be um really just kind of like the the basics of how to think in terms of working with these AI agent teams. And then uh you know the third thing would be hopefully some ideas on how it might help your trading, how it can help sort of your risk management, your research, um coming up with new strategies.

**2:39** · So uh yeah, if you're looking to sort of use AI assistance to help you with your uh investments, I think paperclipip would be a great tool for it. So um I think one of the things that I can do is I can share my screen. So, we can include in the show notes um a like we can include in the show notes a link to how you install paperclipip. It's very very easy. You can just do it with uh one command.

### Org Charts and Agent Teams

**3:10** · Um you can see on our website paperclipip.ng. We have uh the command right here. If you want to get started, just copy and paste this into your terminal. So, um, you can use paperclipip even if you're like not super technical. Um, though, and I would say that we're making it easier every day. Um, but let me show you kind of like the paperclip instance. Let's just give you like an overview.

**3:37** · We'll start a new organization and we can start to set it up from scratch um, and for ways that that might help the trading. So, how does that sound?

**3:46** · Sounds perfect. Okay, great. So, um, this is Paperclip. I use uh paperclipip to make paperclipip. Um when you look at it at first that looks sort of very much like um a kind of project manager.

**4:02** · Hopefully it feels like very intuitive and very easy to use. One of the things that you can do here is you can come here and look at the org chart and you can see here that we've got our CEO, CTO and I've got a number of agents here underneath the the CTO. Um the the coding the coding area is actually one of the biggest departments in paperclipip right now because it's a coding kind of based project. Um one of the important things about using paperclipip is you can bring your own agent.

**4:28** · You can use uh codeex, you can use claw code, you can use open claw, hermes um really sort of gemini pi any agent that you want to use can be integrated into a paperclip organization.

**4:44** · The thesis is that really there's um more and more agent more harnesses let's say being created both sort of open- source ones but then even closed source ones right there you're seeing um tools like a lawyer like um uh like Harvey or coding agents like Devon or Factory and um or the Figma design agent and all of these things um you can hook into your paperclipip organization um and they can communicate with one another.

**5:11** · Um let's see for example um we have uh the marketing department here and I've got uh content strategist, community manager, video writer um and let me give you an example that we're using sort of for our um uh kind of company and and and then we can sort of port the the idea over but I think it's illustrative. Um we on GitHub we crossed 40,000 stars uh the other day.

### Marketing Video Demo

**5:45** · Actually I think right now we're actually about to cross 50,000. And one of the things that I really wanted was to sort of celebrate that with a tweet.

**5:54** · And so you can see here um we've got this like video where it says oh celebrating 40,000 stars. And um one of the things that I really wanted is I thought, "Hey, I don't want to just post a screenshot like I would have a month ago. I want to actually have an entire video." So what I did here is I went and I asked uh my CEO, I said, "Hire a video writer and ask her I'm not going to type it all out and ask her to create a marketing video celebrating uh 40,000 stars."

**6:26** · So, what I did there is I asked my CEO to hire a new video editor. Um, and then I asked it to give her the um the skills to make a video. So, um if you've used agents um already, you might be familiar with this skills.sh website um right here, which has um a lot of skills that you can use for your agents.

**6:52** · There's a really really popular one number five remotion best practices which gives your agents the ability to do these kind of uh videobased skills.

**7:01** · And so um there's a skills manager built into paperclip. So you can ask your CEO to do things for you. The the analogy of paperclip is that you are the um the board and you ask your um CEO to basically do things for you. You ask your CEO to sort of act out in uh in the app and and do what you are asking. And so in this case, we ask it to hire a new employee.

**7:32** · We ask um him to give her the skills to be able to use Remotion. Um, and then you know they're automatically hired. And then what I uh was able to do is I is made an issue for the video editor and I said uh plan a video for the stats dashboard. So go look at the dashboard and our stats. Look here. I didn't even spell this properly. Make a plan for a reotion video that can celebrate 40,000 stars etc. etc. Right?

**8:00** · So what's happening here is I was able to just write like this one short paragraph and get a whole plan. 40,000 stars stats. Um, you know, and it wrote out the plan and I read it and sort of edited it from there. Um, and and really what I when I actually read the plan, I wanted some feed I wanted to give it some feedback. I said, "Well, your cuts need to be 2 seconds, not six." And um, have the 40,000 stars be animated and all these things. So, so we had a bit of a conversation back and forth over four or five minutes.

**8:31** · And then well at the after it was done this video that you see was basically created. Um and and and so the answer is like how and and couldn't you do this with cloud code already? And the answer is like yes you could do this with cloud code already but let me point out some interesting things which is one this prompt is is quite short like why why did it look so good? Well one because within the paperclip organization we already knew um where the dashboard was. we could at mention another project where we had built the pro the dashboard previously.

### Why Orchestration Beats Solo Agents

**9:04** · Um two we we have access um configured already for these agents to have access to our internal stats and our dashboards. Three, we have a branding guide um already created that the organization like knows how to find.

**9:21** · There's already a paperclipip branding guide. So when you ask it to make sure that it's on brand, it understands this institutional knowledge. Um and and so because you have this the like all of this company knowledge built into paperclip, something that would have taken you maybe half an hour, 45 minutes to sort of copy and paste into your claude code um either like command line or into the cloud code app becomes something that's almost like an afterthought.

**9:49** · One little paragraph and now you get this incredibly high quality video that is like super high context to your business. So even though you might not be making videos day-to-day surely you can see the general pattern which is you can multiply this sort of leverage across your entire business um because or across like your your your your trading and your knowledge workflow because it understands how you do work

**10:13** · and it keeps um this conversation now is a memory um so when I come back later and I want to do another video you're able to um like go back and make iterations on the same video or also learn from how we do videos.

**10:28** · So, for example, we've done a couple other videos with this video editor and and let's say that for example, I always notice that kind of uh the default option with Claude is that it's um it always makes the cuts too long, right? They're always six seconds instead of two.

**10:47** · One of the things that we do is you run over um you you can run over the history of your video creations and and learn sort of the principles and the styles of what you're doing um and and make it so it does it right the first time next time. And so I think that's one of the key things that is like important for um success with these kind of agent tools is this idea that like you need to give them your taste, right?

**11:19** · Because these um agents while they can create anything, they can't know what you value. You have to be able to sort of imbue your taste. So this would be um kind of a first layer of some of the things that you can do with paperclipip. Um there are um so so yeah so this is an existing sort of instance.

**11:41** · We've got an org chart with all of these different agents that have kind of different personalities. Um we've got projects here which we can configure for different ideas that we're working on.

**11:52** · You can set up routines. Um, so for example, I use Twitter book bookmarks pretty heavily in order to kind of capture thoughts that I'm interested in day-to-day. And I have a routine here where um what I ask it to do is every day sync all of our bookmarks.

**12:13** · And then I have some guidelines in terms of um what I expect and how I want it to um capture these and um and then uh write a report for me and then I can sort of see each day all of the the things that I've bookmarked and um ways that they could be helpful for paperclip. Um, so for example, we could look at some recent runs.

**12:44** · Um, and we can see here that we've got, you know, highest value moves, build a lightweight execution adapter, um, you know, productize memory, all of these things. It talks about, you know, the new mem palace that was going around Twitter.

**13:00** · And um in this version right now all it does is create a report but really in the future versions there will sort of be like actionable items here where you can say like oh I love this idea I want you to like build it create a create a new issue right um so you know is open source and it's pretty young we released it on March uh 4th it's now April 8th so we're about 34 days old uh give or take.

**13:26** · Yeah. And so these would be some things that we're work working on making like giving this kind of more interaction.

**13:32** · Yeah.

**13:32** · So when I think about this from a trading perspective, you're you're you're trying to make some money in the markets. You are just one person. You now have this capability to not just be one person, but you will now have to expand your mind beyond you. Um so you have to assume the role of coordinator and knower of all things.

**13:57** · So um a a lot of the time these roles because in my experience from it they they can determine what their roles and responsibilities should be but it's going to be so much richer if you can input your taste as you have said. So when I'm thinking about this from a a trading perspective and trying to make some money I think a lot of the time we uh pull in our information and knowledge from other places.

**14:22** · So I imagine a world I use bookmarks all the time as well on Twitter, but bookmarks in the trading world might not necessarily be of much use, but what might be of use is for example pulling all the transcripts from a YouTube channel and and determining what the strategy is and um and then

**14:44** · maybe you pull them from five different YouTube channels and then compare them and see what are the similarities and how could we build a trading strategy based on that and what you're suggesting is that these agents could essentially meet together and talk about the similarities and pull the transcripts and do that all for you.

**15:04** · Yeah.

**15:04** · So, you know, maybe we could work on we could try to do something like this. So uh you know we can call this Lewis Ventures and it's um an automated like trading hedge fund um you know where we trade uh maybe we trade you know crypto or traditional equities we can sort of configure it. So the first thing that you do here is you come in and you name your company.

### Research and Reporting Agents

**15:30** · So this is what you'll be greeted with when you kind of uh start the onboarding process. you can create your first agent. Right now the first agent we suggest is a CEO. I think in soon you'll do more kind of teams right rather than sort of the uh uh always running the entire company. I think both like cloud code and codeex are good defaults for your CEO. I do think it's really important that you choose um a frontier model for your CEO. You're going to have a better first experience.

**16:00** · Um, as things stand as of recording, you can use um your subscriptions both through cloud code and codecs. Um, at right now in the news is sort of a bit of like ambiguity around what counts as a harness I suppose for especially cloud code.

**16:19** · Maybe you've seen this around openclaw at the moment. um claude code like paperclipip runs using the claude code um sort of uh harness on your local machine um and such so that you're able to use your subscription billing at the moment for with paper. Um so if you come here uh we'll hit next. It runs an environment check and yeah so now you want to give your agent something to do.

**16:50** · We'd say, "Oh, hire your first engineer and create a hiring plan." Um, you know, maybe you want to fi have founding engineer, maybe you don't, right? I don't know that we necessarily want an engineer at first, but um, you know, whatever, we can try it. Um, and let's say break the road map into concrete test, start delegating work. We need probably specify this a little more and say um, we like like what do we want to trade like what venue do we want to trade on? I think the the the more detail we can give it in the outset, the better results we're going to get.

**17:20** · Like, do we want to trade on hyperlquid, you know, trade in crypto?

**17:24** · We want to watch YouTube channels, do we want to trade sort of traditional markets? Lewis, what do you think?

**17:30** · Um, let's say we're going to trade in Bitenser. Do you know about Benser?

**17:36** · Bit tensor?

**17:38** · Yes, Bit Tensor.

**17:40** · Okay.

**17:42** · Uh, yeah. in in the Bit Bit Tensor uh ecosystem.

**17:48** · Okay, great. You know, I don't I've actually never really used the Bit Tensor ecosystem.

**17:51** · My goodness. Watch some of the videos I've got coming up.

**17:55** · It's going to be it's mindblowing.

**17:58** · Um so, plan around that. We'll need to uh develop strategies.

**18:07** · Um strategies.

**18:10** · Let's see. We we we should have some some some transcription here. Let's see if this works. Um we need to have back testing. We need to have data gathering. We need um to write the trading execution layer. And we need to be able to retire old strategies if we find that their edge is degrading. And and we need to log it all for accounting.

**18:36** · And we need to log it all for accounting. Now you can fill out here really as much or as little as you want, right? This is just kind of our agents first task. Um, but now that we sort of have this, we will like create this and launch it up. So, um, this sidebar that you see over here are different, uh, companies that you can run within Paperclip. Um, and yeah, you can see right here, this is the one that we're working on.

### Onboarding and Setup Walkthrough

**19:04** · Um, I have some others that And well, what we're going to do here is we're going to sort of let our CEO uh run. He's going to do his work. He is reading his reference files. He's doing his thing, right? So, let's just let the CEO work while we kind of uh talk more about maybe some of the more advanced features. Let's let's hop back over to um the paperclip company while this works and we'll come back.

**19:36** · Um some of the other things that are like a bit more advanced in uh paperclipip is this idea that you often want to have um a bit more control around uh like verifying the work. So for example, one of the things that you're able to do when you create a new issue is you can actually set up reviewers and approvers.

**20:07** · Um this is one of the key workflow design patterns that are really that's really important in agentic workflows is this idea that you might have um that when a task finishes, you probably want another agent to review the original agents work. Um, of course, as the underlying models get better, like having them check up on each other maybe will become less relevant in a few years as the models are are stronger, but for now it's incredibly important that um you you you have review for your critical work.

**20:39** · Um, I think that the um the the downside of course is that you pay extra in terms of tokens because now not only are you paying to do the work, but you're also paying to sort of verify the work. But I think for any kind of like critical workflow like it is in most of our sort of like trading work, you definitely want those sort of um checks and balances.

**21:03** · So, if we're saying, you know, I want you to go out to YouTube and and transcribe the video and come up with trading strategy ideas, that doesn't necessarily need this kind of like intense workflow and approval.

**21:14** · But if you're saying like, oh, I want you to sort of verify the back testing hygiene of this strategy and then make sure like the red team verifies that, you know, that the um kind of edge holds in adversarial situations and then like we sort of have risk management sign off on it. When you have these kind of like more elaborate and more like missionritical pieces, you certainly want to be a be using these kind of like reviewers and approvers. Even in like web development, you'll often use this for QA.

**21:45** · That's like a simple case where it's just like build this feature and have QA look at it and make sure that it's right. And one of the key things that you need to do is you you need to make sure that you are managing your skills as you go. that the um you need to make sure that you're like giving your agents the capabilities necessary um to do their work on the world.

**22:15** · So what I mean is um if you're going to have QA verify how uh like that a feature works, you need to give it something like the agent browser skill. So, that's one of the like main skills that you can get here at um skills.sh. Yeah, the agent browser skill actually gives your agent access to a browser.

### Building a Backtesting Ideas Team

**22:40** · This is also very useful when you need it to sort of navigate the internet. Um, all right. If we look back over here at Lewis Ventures, we can see that um we have this uh pending request from the CEO to hire a CTO. So, we're going to approve this. Um, and now that he's Yeah, there we go. All right. Now, here is also a hiring plan and technical road map.

**23:09** · Um, well, let me finish my previous idea, which is that this idea that you need to give your agents tools, which is to say a key thing that you want to be thinking about when you use agents is how do I wrap what they're doing into a skill?

**23:26** · you as an agent operator should always be thinking about um what skills you need to give your agents to do their work. And so um you know if I was executing trades on hyperlquid I might have both like some hard code and a hyperlquid skill or I assume we'll have similar on bit tensor or um if you're like doing trading on the Ethereum chain or in your Charles Schwab account, right?

**23:53** · like every time you sort of have these different kind of instances where you you expect your agent to do something on a regular basis, you want to create um skills for that.

**24:05** · Of course, we talked about there's a skills manager built into paperclip when you sort of submit uh you can use slash to reference your skills if there are skills you express expressly want your agent to use. Um, yeah. So, so that's a key like like I don't know like like point in in using agents is write skills for your agents. You'll you'll find that your work is a lot better. Yeah.

**24:30** · The kind of thing that I think about when I think about assigning skills or or or thinking about processes that repeat and then making skills from them is that my immediate thought was well I'll just make a skill guy as one of the agents who who kind of tracks what everyone's obviously this is racking up the cost.

**24:52** · Uh but you kind of it's almost like a verifier where they look at all the processes that keep getting done by the agents and then say and then just automatically put those into skills.

**25:02** · I 100% agree. That's something that we've built even in the paperclip organization is we actually have a skill consultant here. Um and that's his job especially when we find cases where um some of the skills that we have aren't working so well. Um, so for example, right here we're saying, you know, validate the Q the QA browser has agent reliability. Why can't he access the authenticated instance? And so he's he's actually an agent within our org that that goes and refines skills.

**25:30** · I'll tell you what, this is an idea that has been showing up so often, we're actually integrating it into paperclipip core where it will just sort of be a background process that runs for you automatically where it sort of surfaces to you saying, "Hey, these are some things that we've realized your org does all the time and you need these skills and um but today if you download the version that we have today, um what you're suggesting is exactly right.

**25:56** · It's like make a skills kind of agent whose job it is to periodically reflect on how your org works and and and and pull those out.

### Adding a Risk Management Layer

**26:09** · Okay, so we have got a few uh things are starting to work now. We haven't even read our technical hiring uh road map yet and our dashboard is showing there's actually six live uh tasks coming in. So if we look at these issues um wow the the the CTO has already decided to architect and build the training platform um building out metrics the market data collector the bit tensor subnet data collector and the product scaffolding.

**26:40** · So you know we probably need to come back and look at these plans before we just let them run with them. But hey we asked our agents to do the work and they're doing the work. So let's look here the foundation one the CTO is submitted um we need the core infrastructure which is the CTO's first sprint and then there are future hires as the CTO identifies these needs.

**27:02** · So this says in this plan it said uh hiring decisions for phase two three will be driven by the CTO's assessment of where the bottleneck is after phase two is under way.

**27:16** · Yeah. So one of the things that we have here actually you can see is that these are all cued by default. The agents only will run um one at a time. We are able to set the um where is it max concurrent runs. We could set this higher to let's say like three or something. Um I'm not actually sure if these cued runs will kick off.

**27:43** · This is probably a bug presumably like after I change that these should all unc start working. Frankly, I think there's a bug and it's not going to do that. But I'm just letting you know that you can actually configure these to run more than one at a time. Um I guess we're just going to have to wait for this to run serially at the moment.

**28:04** · So the so the way you're interacting with paperclipip there is very much like for lack of a better word website interface.

**28:16** · Mhm.

**28:16** · And then you're you're you're kind of just using it like that. I how I maybe I'll share how I've used it because I'm sure you get all these different ways that people have been using paperclip. Essentially, I created a almost like a I I used paperclip in my uh terminal.

**28:39** · So, um I ended up just ultimately ended up creating like a like a a local host, but it just records my it transcribes my voice, and then I'm just talking to it as this like big brother type of guy to my business. Um, and then it goes into the back end of paperclipip and just does all of this for me.

**28:58** · So, um, you know, I was I I like to kind of like sit in my chair, sit back and just just brainstorm this whole thing like, yeah, I want a quant team, and this quant team needs to be split up into three different departments. And this one department tests uh outlandish strategies, and this one tests kind of moderate ones, and this one is more safe. And then we're going to iteratively test all of the strategies that we put together. And this is going to need this different person and this different person.

**29:28** · I'm just talking freely at it. And I'm saying and I want all of them to be doing it all at the same time. And that last sentence that I said there kind of I I noticed it now cuz I had I had 60 or so tasks issues running at the same time.

### Giving Agents Clear Instructions

**29:45** · Yeah.

**29:45** · and they must have in the way I used it because just kind of gone into the back end and changed that setting um you know to to do that automatically because I didn't realize it wasn't there by default. So um I just I I kind of went over to chat GPT um and I also just talked freely to chat GBT to say can you or like organize the architecture for this entire organization with all the roles and responsibilities. So I can give that to paperclipip in my terminal.

**30:19** · Um and then it and then it just spun up the 32 things all at once and it created the bit company and everything. Um so I didn't do any of the manual clicking uh which I thought was uh maybe a maybe an interesting way to use it. Um yeah, I love that. I love that. And so um what what agent harness were you using? Was it codeex cloud code? Like what in your terminal was sort of doing the work? Cloud code. code. Yeah.

**30:46** · So, so that's a really important and powerful like piece of paperclip, which is that everything you see here and a lot of things you even don't um has an agent surface. There is a paperclip skill included with paperclip um that's

**31:03** · that has documented all of what can be done. creating issues, closing issues, adding comments, creating projects, artifacts, um, goals and hiring and skills, and every piece of of paperclipip has an agent surface such that if you're more comfortable just running it through your clawed code as kind of a CEO, you can 100% do that. Um, I'll let Yeah, I just I found it useful to have paperclip in the way that you're looking at it just to see what was happening.

**31:32** · It's almost like this was the inner working and I was engaging with it somewhere else.

**31:37** · Yeah, it's kind of interesting.

**31:39** · I I I love it. And so something that So I think that's a good way to use it. A second way that people are doing it is they hire a um open claw and they will use that open claw also as their CEO. So then they can talk from Discord or Telegram or wherever they want. You know, I think it introduces some kind of variance in terms of how good your open claw is and like now you you're going through open claw. So, but for the most part we have sort of good kind of reports. Hermes people do the same thing.

**32:09** · Um and then and then we are also working on sort of a firstparty like paperclip agent that will be kind of built into the app. So you can kind of have like a chat surface to to just talk within the app which will be really important for to do similarly what you're talking about.

**32:26** · Um so yeah and I think and then really like part of what we're trying to do is to make it such that the um that the experience that you get as you get more sophisticated with paperclip um

**32:45** · is you'll find paperclipip will be the best like the UI will be like one of the best ways that you would want to interact with it when you're kind of doing active work but then at the same time the underlying agents are getting better and the kind of control plane is getting better such that you don't have to micromanage it as much. Right?

**33:01** · So it's this kind of like dual this like barbell strategy where the org model is trained well enough to to act independently in a way that is predictable predictable but then you can also sort of like dip in adjust plans course correct you know while you're like when you need to.

**33:23** · Yeah.

**33:23** · So, so if you're kind of envisioning how this looks, let's say we had four hours to set this up. When we get to that end point and we're we're looking at this thing run, what what what where does your mind go in terms of like the full capability of this thing?

**33:42** · Specifically for trading, I think that the first thing that I want is um like a back testing ideas team. So what I would essentially set up is I would have a set of researchers whose job is literally like every night what I expect you to do is like come up with ideas for new ideas that we're going to to back test, right?

**34:08** · Um, I would sort of either have I would give my agents a set of sources like I would say go look at archive, go look at YouTube, go look at Trading View, go look at like I would come up with I would even have my researcher research an area of maybe 20 or 30 different sources of alpha that I can think of and I would say like um go to all these places and come up with new ideas.

**34:37** · I would also ask them to set up um a workflow so you can remember of all of these kind of like uh back testing strategies or ideas that we have. I need you to make sure that you keep track of which ones we've already tried and what the results were.

**34:53** · You can almost think of like each strategy as almost like um an initiative or an effort, right? like you know something stupid like oh if I'm I want to test like the EMA crossing of these two time frames like for the most simple hello world example you would um

**35:11** · you want to make sure that your entire system is kind of tracking from the outset like how like what was good what did we try what did we use what did we discard right um and so that would be the very first thing is I would have this kind of like idea generation inflow which is either like one team for generating ideas or potentially two teams like one that's like researchers and the other that sort of distills. It just depends on your needs. Um yeah, on my on Oh, yeah. No, carry on. Sorry, I'm I'm interrupting.

**35:41** · No, please.

**35:43** · Well, well, on on the on the channel recently, we've been I've been guiding people through the process of actually setting up your own uh trading agent.

**35:50** · So, it actually makes the trades for you. So you build you build a strategy with your whole kind of I don't know it's it's I guess can be quite complex or it can be relatively simple but it will essentially only trade when the confirmations are all aligned and it will sell and the c and with certain criteria and I'm I'm interested now because yes it would be good to have a research team and they're iterating on these different strategies you know they might be pulling this week we're testing the moon phase uh versus you know the

**36:23** · oil in Iran or something and using that to try and piece together a strategy and it's making it better every single time. But adding an execution layer onto that is like the real the real game changer cuz once you can in my in the organization that I set up there was a whole process for risk management. So um there was a team for risk management.

**36:44** · They did a whole bunch of different things, but one of their roles was to delay the um switch from paper trading into real trading until they saw certain m metrics were met with the paper trading and then they would slowly deploy capital um from then like a real firm.

### Real Results and Lessons Learned

**37:01** · Uh and so they're operating in that way and then it's like oh wait we should actually elevate this now to paper trading with that moon phase and oil strategy that we created and it's actually going to the agent that we've already created on the channel to to just go and do the trade.

**37:20** · Um it's kind of you know it's one thing doing the research but it's another thing getting the thing to actually trade the money. Uh, and that's so exciting if you can find a strategy or or create a strategy that has a, you know, a high sharp score and very low draw down. And if you can get one that actually makes money like profit, even if it's just a scent, like you're making a scent, it's it's it's if you can make a scent with a trading strategy, an AI trading strategy, you're doing well.

**37:48** · Also, it's very hard to do it. But how hard is it to do it if you've got a team of 20 people doing more research than any human could do? Um, kind of puts it it puts you in a position where your the odds are in your favor kind of or more in your favor than they've ever been. I guess that I would also say that like the best results you're going to have with Paperclip um and probably a lot of other agent frameworks are like I wouldn't really scale up faster than you need.

**38:21** · Like like I think if you sort of come to Paperclip and you do sort of create 30 agents on day one, you're not going to get great results and it will be like too expensive and too slow. I think that like the best way to do this is to start small and I would actually kind of hand create my initial team. um

**38:42** · where um just try to keep it as simple as possible to your like system which would be like research back test I don't know like red team execution and like risk management or something like I would probably just have those six in the beginning maybe something around like deployment um and

**39:04** · and then like or maybe even less like really you just add new agents as you need them and as things are kind of like Well, it's like you you just have one agent and it's like working and then from there what you do is when it starts to kind of break then you break pieces apart or when you kind of need more sort of back and forth between them. Um I think that's going to be the right approach is build it up.

**39:23** · As much as like it's really incredible to kind of like wave your hand and then have a massive team, these agents will perform poorly if you don't take the time to really train them deeply in terms of like your values and your instructions. And so like in here, I would go to instructions and like fill out Yeah, this a the CTO doesn't even have any instructions at all.

**39:47** · And you certainly need to fill that out. like even for my own um kind of like instructions for my coder um this is really growing quite a lot every day um in in how I expect it to sort of operate. And so you you you have to do that and you have to kind of like have um you really want to be on like solid footing before you like fan out too broadly I suppose is what I'm saying.

**40:16** · Yeah, you're you're absolutely right cuz what I what I saw was on on X I just saw this complete flood of people doing some crazy stuff and I was like okay how how can we push this to 100 immediately and you know I found myself and you're you're right I found myself creating agents after the fact to optimize cost uh and then I

**40:39** · found an a I had to get an agent to look at people who were doing redundant jobs and I I kept having to do these things to like patch the holes that just doing a blast of a agents is obviously going to create. So, um yeah, putting meaningful time into your agents just like you would real people if that you were depending on these people to generate you money. Um you just I guess you do have to give that time.

**41:02** · I was building a uh hyperlquid trading bot before I started payclipip and it had it was like making some money for it was making pretty decent money for the first kind of two to three weeks. It was discovering it was run a nightly lab where it would come up with about 30 strategies and then back test them and then we would eventually promote them.

**41:26** · So we eventually went through um several thousand strategies and landed on kind of three or four that we found were working sort of within that regime and um and it started to work really well until kind of I was using open claws the sort of harness um and and I had built trading bots before and I've been kind of like like it's not easy right it takes sort of a long time to kind of get your you know back testing hygiene right and the execution right? And all these things.

**41:57** · And so, um, I'm not trying to say that it was like immediately a money printer. I'm saying like I've been working on bots for I don't even know how long, like well over 10 years. And so I was able to kind of use OpenClaw to come up with a new version. And what basically happened to

### Treating AI Agents Like Employees

**42:14** · me with OpenClaw, great piece of software, love it, super fun, but like I just wasn't able to manage the details of the project and sort of like dip in where I needed. and it just started started to fall apart and basically lost all the money that it made and I I'd try to correct it and put in these constraints and would skip cron jobs and forget things and like wouldn't do the checks that I had. You know, there was even this weird situation where I started writing code that would force the um the risk management.

**42:41** · So, for example, um like you want kind of your your your you know uh your portfolio has like exposure to where like oh you know we only want this much you know beta exposure to Bitcoin or something and and and and you put in these like portfolio level risk constraints and um and what I realized was that like the LLM would sometimes forget those constraints and not do them.

**43:10** · So you have to actually put stuff like that into hard code. Um, and so I basically had like an API like another service endpoint that would enforce the risk constraints and that worked really well until my openclaw figured out that it could redeploy the service for risk constraints.

**43:30** · Wow.

**43:30** · Right.

**43:30** · And then like it would just circumvent them anyway because it would just redeploy if it didn't like what the risk constraint was. And so there's this like there's definitely these like things you have to be super careful about like your you you can't little have an LLM um even have access to your um your hardest constraints because if they can redeploy it, they can just circumvent it. And LM are like little children, right?

**43:57** · Like one prompt injection and then they'll like steal all your money and then apologize, right? So you you do have to kind of like be careful about um make sure you're building those like know what's good for an LLM and and what's not.

**44:14** · Exactly.

**44:14** · Yeah. I I attention to detail.

**44:19** · Take care of these agents that you're the time and attention. Give time and attention to them. Be thoughtful about what their roles are and that would be the ultimately the the best basis to start from the foundation. Um, so where did we get to? I know you've got a hard stop, but where did we get to with the the simple prompt that we gave at the beginning?

**44:39** · Yeah, let's see here. So, we've got um you know, I wonder where it even put the code for these things. Look at this.

**44:46** · Like, I'm going to like where's the code?

**44:54** · So, let me tell you one thing. Paperclip is not a code review tool. the the goal with paperclipip is that you are managing your like business outcomes not pull requests. So that is another kind of like important piece to understand when you're using paperclipip is it assumes that if you're um that you're

**45:15** · using external tools like in this case if you're writing a trading bot surely you are going to want to look at the code once in a while and it assumes that you have cursor and you have a git repo and you're using github and you like use github and cursor to manage your pull requests. Um, while there's tools here for like helping your like code review process certainly in managing work trees and all of that, um, it's it's it's not designed to be um, a code review tool.

**45:45** · So, um, yeah, look here. So, it's helping us figure out where the code actually is. Yeah, the code is yeah, committed locally on master. Thank you. That's very, very helpful. Really, what I'm looking for here is a file path on my machine.

**46:00** · Here's what I'll tell you. We are working on better results. Yeah, here it is. Here's the folder. We are working on kind of better uh workspace support within paperclip such that um you know what we just went through is a bit more straightforward. But here I can show you the uh code that we have in cursor if if that's useful. Let's see here. How do we share our screen? Let's switch windows.

**46:31** · I think it's just magic for people when they see this stuff and then this for me it was kind of my like magic when I was talking to claw code for the first time and then I see that it's actually created f folders and files and stuff in the background. It's written all this stuff in there and you just don't know because I I come from a zero development background. Everything I've learned has been purely from vibe coding.

**46:55** · Um, it's just fascinating to me to know that I've said something and then I mean it initially it was just fascinating for me that a file was created it not in the traditional way where I've just rightclicked and clicked new folder new and then you know haven't done it manually. It's just kind of amazing and then it's obviously it's just on steroids now.

### The Future of AI Agent Teams

**47:17** · Yeah.

**47:17** · So we've got here in cursor this kind of like rudimentary back testing engine. We've got um some you know basic metrics like sharp ratio and optimizer. I think that like look that your results yeah here's a simple moving average cross strategy. Your results are still very much going to be dependent on your ability to articulate the degree of like professionalism that you expect.

**47:49** · How I would really do this is I would have um I would do a lot more planning around what back testing library am I going to use if any like are we writing our own or are we kind of using one off the shelf. There's a there's actually quite a lot that are super good that that maybe you should be using instead of writing your own. Um there's a lot of like trading bots that are that are decent and open source.

**48:16** · Um, you know, I think it just depends on where you are. Like if you're kind of like I would rather sort of, you know, use a a well- tested back testing library that I find on GitHub or whether you want to kind of like write it from scratch in Rust or something because you're super hardcore, the more kind of guidance that you can give your agents upfront in the planning phase is going to help, right? um the the idea that you might be able to um uh

**48:47** · yeah, so that's my overarching sort of suggestion is like you now have the power of superhuman AI at your fingertips. Sign up for a GPT pro plan, $200 a month, and um ask it on max pro

**49:05** · mode what some of the strategies are that you should be looking at, what your workflow should look like. and um a and use like what what does good data hygiene for back testing look like and make sure that you enforce that rigorously, right? And so make sure that you are injecting kind of those values and to the the maximum amount of professionalism that you can in your planning and then that will show up um in your agents. Um there's there's kind of no silver bullet there. Just make sure that you're kind of um yeah, planning de with detail. Yeah.

**49:37** · And and and and just just to kind of close this out, just an an idea, if you got a if you can find a really successful open-source strategy on GitHub, you can just give the GitHub to an agent in in Paperclip and say, you know, use this as the baseline and let's paper trade some testing to see if we can improve it in some way.

**50:02** · That's right.

**50:02** · And then you're making your own thing on what somebody else has has made. It's almost like, you know, you made you made paperclipip and it's incredible, but people have their own specific needs and they're building their own things on top of it and you it's it's just it's so collaborative and I I really am enjoying this phase of where we are right now in the world because uh it's going from,

**50:25** · you know, in in in crypto, we went from this is a decentralized thing and it's so exciting all the way through to now basically crypto for the most part is going to be used centrally.

**50:36** · um you know the big banks are going to be running it and it's all going to be is controlled in many ways you know it it's gone from decentralized to centralized um and I'm seeing AI now kind of move from centralized to decentralized um and that is kind of fun like it's collaborative you can make improvements on things are already good um and you can use good things as well you just have to have a little bit of technical knowledge I guess to to get it done. But look, Paperclip is an incredible addition to the ecosystem.

**51:08** · It's been so much fun using it and I've been watching your interviews elsewhere as well. So, um, thanks for giving your time to all those interviews and mine.