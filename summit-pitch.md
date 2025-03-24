# Summit pitch

Questions: who shall be the person that pitches?

## Title
*The title of your talk/discussion topic. This will appear in the Language Summit schedule on the conference website.*

Fearless Concurrency in Python


## Key discussion item

> *What is the "thing" you want to discuss in front of mostly Python core developers? What decision to be made? What are your questions, and proposed solutions? This should fit in 10 minutes, to allow for 20 minutes of discussion. Therefore this should be very focused. This field will only be read by Language Summit co-chairs to determine the talk acceptance. You can include a rough outline, useful links, sample discussions, etc.*


We want to discuss a dynamically checked concurrency/ownership model for Python.
The concurrency model is based on "regions" and "deep immutability", and allows existing Python data structures to be used in multi-threaded programs.

The presentation will be based on the ideas presented in the PLDI'25 paper (link to be added)
and prototyping work done on a fork of the CPyton interpreter.

The aim of the presentation is to get feedback on the ideas, and to discuss the implications of the model for Python.
Getting something like this into Python would be a big change, and we want to discuss this with the core developers.
We will also discuss how the model can be implemented in CPython, and what changes would be needed to the language and runtime to support it.


## The public pitch
*This will be shown in the Language Summit schedule on the conference website and published ahead of the event. Write one or two short paragraphs to pitch this topic to the attendees. This is your chance to encourage people to discuss the topic with you!*

With the move to free threaded Python, the challenges of concurrency are coming to Python developers.
The race conditions that are common in concurrent programming are hard to debug, and requiring different tooling to is commonly used in Python.
We believe there is an opportunity to build a new concurrency model for Python based on "regions" and "deep immutability".
The goal is to provide a model that is easy to use and flexible, so existing Python programs can be easily ported to multi-threading.
The model allows for safe sharing of data between threads (in free threaded Python) and sub-interpreters.

The presentation will be based on the ideas presented in the PLDI'25 paper: (link to be added).   

