---
title: "Claude Code + NotebookLM + Obsidian: Super Skill Pipeline"
source: https://www.youtube.com/watch?v=kU3qYQ7ACMA
author: Chase AI
published: 2026-03-06
created: 2026-04-11
description: "Building full-stack AI workflows: YouTube search → NotebookLM synthesis → Obsidian wiki. Self-improving loop via CLAUDE.md updates."
tags:
  - claude-code
  - notebooklm
  - obsidian
  - workflow
  - pipelines
  - chase-ai
---
![](https://www.youtube.com/watch?v=kU3qYQ7ACMA)

Building full-stack AI workflows: YouTube search → NotebookLM synthesis → Obsidian wiki. Self-improving loop via CLAUDE.md updates.

Chapters  
00:00 Introduction  
02:00 YouTube Search Setup  
05:00 NotebookLM Integration  
08:00 Obsidian Pipeline
  
Claude Code + NotebookLM is amazing. Claude Code + Obsidian is free value. The new Skill Creator is legitimately game-changing. So what happens when you combine all three?  
  
In this video, I walk you through a practical, repeatable workflow that turns Claude Code into a full-blown research agent — searching YouTube, running deep analysis through NotebookLM, generating deliverables, and organizing everything inside an Obsidian vault. All of it set up in under 30 minutes.  
  
This isn't theory. This is the actual system I use, and you can take it and apply it to whatever you research, whatever you need analysis on, and whatever deliverables you need to create.  
  
⏰TIMESTAMPS:  
0:00 - The Power of Three  
1:32 - The Workflow  
5:23 - The Setup  
9:36 - Executing the Workflow  
13:44 - More Resources  
  
RESOURCES FROM THIS VIDEO:  
➡️ Master Claude Code: https://www.skool.com/chase-ai  
➡️ My Website: https://www.chaseai.io  
➡️ notebooklm-py Repo: https://github.com/teng-lin/notebooklm-py  
  
#claudecode #claudeskills #obsidian #notebooklm

## Transcript

### The Power of Three

**0:00** · If Claude Code plus Notebook LM is amazing and Claude Code plus Obsidian is free value and Claude Code plus the brand new skill creator is legitimately gamechanging, then what's going to happen when we combine all these tools together in a practical yet simple to setup workflow that you can start using today in under 30 minutes? Well, that is exactly what we are going to find out in today's video as I show you step by step how to create one of the most powerful workflows inside of Claude Code. This workflow turns Claude Code into an absolute research monster. And this video is also pretty much a capstone of everything we've talked about in the last few videos because we've covered things when it comes to Claude Code and Notebook LM and Cloud Code and Obsidian and Cloud Code the new skills creator.

**0:44** · But here's where we take all these lessons and we synthesize it into something that has practical value. And on that note, what's important isn't my exact use case, right? This is a personal chase AI use case, right? and how I do research for my content. But you're not a content creator. You probably have a real job. So, what I want you to focus on throughout this entire lesson isn't the exact intricacies of how I'm doing my YouTube search. You should be focused on how do I swap the YouTube search for whatever use case I have and whatever source of information I need, whether that's PDFs or articles or text or whatever, right?

**1:18** · How can we fit in this template into your life? That's where the value lies and that's what I want you to focus on.

**1:24** · And it's also something this is great at, right? This is a very f flexible workflow that can adapt to your needs and we love that. So what the heck is this workflow going to be doing? Well, like I said, this is research on steroids. So we are going to be inside of clawed code and we are going to do some research via YouTube, right? My source of data in this case is going to be YouTube videos. To do that, we will use a specific skill. From there, we are going to send that YouTube data to Notebook LM via Claude Code. Notebook LM will do analysis on those videos for us.

### The Workflow

**1:58** · Notebook LM will also give us any deliverable we want, whether that's a podcast or a video or an infographic or a slide deck and then it passes all of that back to us inside of Cloud Code.

**2:09** · All of this is executed through skills.

**2:13** · Furthermore, we are going to combine all those subsklls into essentially one super skill. We will do this using the skill creator. Right? So that's where the skill creator comes in. And obviously the notebook LM stuff will come into play here. What about Obsidian, right? Because this is good in a vacuum, but like we kind of want to supercharge this. I'm probably not just going to run this workflow one time.

**2:37** · Well, enter Obsidian. All this data we analyze and more so than the individual data, the way we attack the data, how we like our analysis done, what we want the deliverables to look like, how we think, all of that will be recorded by clawed code in a series of markdown files, a series of text files that Obsidian will be able to take a look at because this is all going to happen in our vault.

**3:01** · Now, looking at Obsidian right here, the vault's great, right, for a couple reasons. For me as the human being, I have great insight into what's going on in my text files. I can click through the files. I can see how they link together and I get cool and neat little graphs. But more importantly, inside of Claude Code, all those markdown files are transparent to Claude Code itself.

**3:19** · It's easier when it's set up in this obsidian sort of format for Claude Code to find the things it needs.

**3:25** · Furthermore, over time, we will be able to refine how Claude code speaks to us and thinks in this manner via the claude.md file, which over time means Obsidian helps Claude code do this workflow in a manner we want. Right?

**3:42** · With Obsidian added into this workflow, we're able to turn Claude Code into like this well-trained personal assistant that executes this workflow on our behalf. And that's super powerful. This almost becomes like a self-improving loop, right? Because the more I run the workflow, the more it gets its analysis in the way I like it, the more I talk to cloud code, the more all that data is recorded. And Cloud Code continues to build and build and build over time.

**4:10** · This corpus of knowledge and evidence for how I like to work. And so that's how we get this like awesome symbiotic relationship and all these things kind of helping one another by combining Claude code with the skill creator with notebook LM with Obsidian, right? And you can see how flexible this is because this sort of workflow changes whether you know you know we could take out YouTube could be PDFs right you could even take out the notebook LMP piece you could really have any workflow here right insert whatever flow but if you keep this template of flow obsidian and improve skills via the skill creator you have something super powerful at your fingertips and it's not something a lot of people are doing now before we get into how we set this up exactly a word from our sponsor yours truly Again, if you want to learn more about Claude Code, I just released a Claude Code master class inside of Chase AI Plus. It takes you from zero to essentially AI dev, regardless of your technical background or lack thereof. Chase AI Plus is great if you're serious about AI and you're trying to make a career out of this thing. So, definitely check that out. Also, there is a free Chase AI community. You can find that in the description. All the skills we talk about today, as well as a number of other free resources, can be found there. So there's something for everybody. So first thing we got to do is create our skills. You will notice I am inside my vault. We have to be in whatever our vault folder is for Obsidian to pick up on this stuff. Now skill creator skill how to install it, get it working. Make sure you check the video above. I go in depth. But the 5-second version, you're just going to do /plugin. You will search for the skill creator tool.

### The Setup

**5:44** · You can see mine is installed right here. Skill creator. Install it. Exit cloud code. Spin it back up. you're ready to go. And so if I want to build a skill, I'm going to do slashskll creator to make sure it actually uses the skill.

**5:56** · And then we're just going to describe it. In this case, I said I wanted to create a skill that searches YouTube and returns structured video results. It should use the yt-dlp to search for videos by query. Return the results blah blah blah blah blah. This is how it is for my YouTube thing. Adjust it for what you want as your source. Again, these prompts will be available inside of my community. Once you run that, it will create the skill automatically inside of yourcloud folder. It'll give you some descriptions about what it did with the skill creator tool. Remember, we have the ability to run tests on it as well if we want to, but we'll skip that for now. So, that gives me the YouTube skill. I can now search YouTube. What about the Notebook LM side? Well, just like the last two things, I have a full video deep dive on that. Check it above, but I will give you the 30 second rundown. So, notebook LM does not have a public facing API. So, for us to connect Cloud Code to Notebook LM, we are going to be using this GitHub repo, the Notebook LM-PI. I'll put a link in the description to install it is very easy.

**6:50** · We're just going to run these commands inside of our terminal. So, we'll just copy this. I create a new terminal.

**6:55** · Again, I am not inside of Cloud Code at this point. This is just purely the terminal. And I will paste them in there and run the install. After I run that install, I need to log in to Notebook LM authenticate. You see it here in the CLI section. So, I just copy that notebook LM space login. Put it in the terminal.

**7:13** · Hit enter. A browser window will pop up asking me to log in. I log in and that's it. You are done and installed and you can now use notebook LM. However, we need to teach claude code how to actually use it. That's where the skill comes in. Now, this repo gives us a command to do it. We can run this notebook LM skill install if we want. We also have an ability and what would probably be better now that we have the skill creator would be to like just copy you know essentially this entire GitHub repo or just put a link to it give that to claude code and say hey use the skill creator to create a skill for notebook LM-PI and you see that prompt right here skill creator create a skill so we can best use the notebook LM skill seen here right like this is like one of the best things about claude code is it will do things that affect its like own use, right? Like it understands how skills work within its own ecosystem. And so when I do stuff like this, it sort of self-improves in a way, which is great.

**8:10** · And once you run that, you'll get the same message essentially that you saw above when we created the YouTube search skill. And when it comes specifically to the Note LM skill, these commands allow us to do anything and more from the claude code terminal that you could do inside of notebook LM normally. So we have the ability to create our own notebook. We can add as many sources as we like. Well, up to 50. It could be from our drive, copy, text, files, YouTube, etc. And then like I mentioned before, we have all the deliverables that notebook can give us audio review, mindm map, flashcards, infographic, etc., etc. So now we have the YouTube skill and this graphic has just become hideous, right? Let's clean this up. So we have the YouTube skill. We now have the notebook LM set up. But again, I don't want to tell Claude Code one by one, all right, do the YouTube skill.

**8:54** · Sick. Thumbs up. Okay, now do the do that skill. Cool. Thumbs up. I want to do this all at once. I just want to turn it into one skill. And that's what we'll do now. We're turning a workflow into a skill. And so to create that YouTube pipeline, that workflow super skill, you can see same exact process. Skill creator. And then I just did a stream of consciousness for it to create that.

**9:15** · Pretty much saying, "Hey, I want this YouTube um pipeline skill. I wanted to use a YouTube search. I wanted to send it to Notebook LM. And I want if I ask for it, some sort of deliverable, and I want it brought back." Right? That's what I said in way too many words. And at that point, it will create the skill, tell you what it did, and then ask if you want to run any evals, which is up to you. And at that point, our workflow is essentially all set up, right? Skills are ready to go. It's inside Obsidian.

### Executing the Workflow

**9:42** · Now, alls we have to do is execute it.

**9:44** · So, let's do that. And in our use case, what we will ask for is we will ask for Claude Code to go search up videos that have to do with Claude Code and MCP. I want to find out the top five MCP servers. So, I wanted to go grab the sources and I wanted to do analysis not just what on the top five are, but how are those videos doing? Like, what is driving views? What are some sort of outliers? What are the gaps? And what can we do to capitalize on that? And I'll also ask for it to take that analysis and create an infographic for me. And that's the exact prompt you see here. I have my YouTube pipeline skill up and loaded. I could have used natural language, but anytime you use the slash command, you know it's going to work 100%. Like I said, YouTube MCP cla code analysis and I ask for an infographic.

**10:27** · So you can see it's starting the pipeline calling the subsklls with notebook LM as well as YT search. And again, the great thing about this notebook LM stuff is the fact that all this processing by the AI is done by notebook LM. Like these are tokens you're not paying for and cloud code doesn't have to use. This is all offloaded to Google. Thanks Google. So after 6 minutes, the analysis is complete. know that most of the time when you're talking about like just like text analysis and you want to know what uh Notebook LM is giving back to you, that's pretty quick. The deliverables can take time. So if you're looking for a full slide deck for example, that can sometimes take up to 15 minutes, right?

**11:04** · Cuz it's several images it needs to create. If it's just like a one-off like an infographic, handful of minutes. So here's our infographic, right? Talking about MCP. Cool. We didn't give it a lot of um guidance in terms of the visuals that we wanted to see, but solid, right?

**11:18** · Subase context 7 playright. All right, breaks it down into autonomous coding and the essential vibe coding stack. So what did they say? Superbase, Figma, Sentry, Post Hog, Context 7, Playright.

**11:32** · Can't argue with that. And then up top, you can see here it gave us the full markdown file for the research. Now remember, this is inside Obsidian. While this seems just like a normal markdown file where stuff is randomly in double brackets, it's a much more it's much more obvious and easy for us as human beings to see this in context via Obsidian. Here's the same document inside of Obsidian key takeaways servers. It has the back links that will show me the other articles it's related to. I can see it inside of the graph, right? Cool stuff. But that's not where the obsidian value ends. Remember the obsidian value is the fact that I have you can see it over here on the left all these markdown files which taken in the aggregate pretty much show claude code how it is I work and if we look over here to the claude MD file and that's what we see right here the cla MD file becomes that brain within a brain right if this vault is the second brain of mine where I have all these ideas well the claude MD file is again the brain within the brain that tells Claude what this all means and what that means in terms of conventions of how to talk to me, how to give me deliverables, how I want things done. And so, like I said, over time, this vault will grow and grow and grow and grow. But it's very easy for Claude MD to grow along with it and again be trained and learn and grow alongside this corpus of knowledge. And it's as simple as telling Cloud Code, hey, update CloudMD based on our latest conversations so these conventions are maintained and you're actually doing what I want to do. And that's as simple as saying, can we update CloudMD so it better reflects my work style, analysis, and output preferences based on our latest conversations? Right? Something as broad as that is enough for Claude to kind of like go nuts with it. If you want to be more specific, you can be more specific, right? That's the great thing about this is it's very flexible and it's up to you. And over time, that relationship between claude code and Obsidian is what is going to cause it to improve its performance, right? Doing that over the course of a week won't have too much of an effect. Doing it over a month definitely will. Doing it over a year and hundreds of hundreds of documents and conversations, that will have a huge lasting effect. So, that is where I'm going to leave you guys today.

### More Resources

**13:46** · I hope you got more out of it than just this workflow in particular and you know a little inside view of how I do my sort of content research because again the big cell here with this is that we can take all this away right and alls we need is some sort of workflow in some manner that helps you right and whatever it is you do and if we can take that workflow and turn it into skills and even turn a mass of skills into a single skill and plug it into this sort of pipeline well then we get the situation where everything is helping helping each other, right? So, and again on the long term, tons of value there. So, let me know in the comments what you thought.

**14:24** · As always, if you want to learn more about Claude Code, you want to check out the Claude Code Masterass, check out Chaseai Plus. There's a link to that in the comments. And as always, I'll see you