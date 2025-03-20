# Summit pitch

Questions: who shall be the person that pitches?

## Title
*The title of your talk/discussion topic. This will appear in the Language Summit schedule on the conference website.*

Deep Immutability for Python


## Key discussion item
*What is the "thing" you want to discuss in front of mostly Python core developers? What decision to be made? What are your questions, and proposed solutions? This should fit in 10 minutes, to allow for 20 minutes of discussion. Therefore this should be very focused. This field will only be read by Language Summit co-chairs to determine the talk acceptance. You can include a rough outline, useful links, sample discussions, etc.*

I want to discuss a PEP for adding deep immutability to Python outlined in this PEP: XXX.
The key motivation for deep immutability is concurrency safety.

A builtin function makes an object -- and all objects it references -- immutable. This notably includes the object's class (and its super classes) but not reference counts. Certain aspects of immutability in Python is rather involved: how to handle functions that capture references to enclosing scopes; how to support subclassing of immutable class objects, etc. There is not a single "right design" so we wish to discuss some of the design decisions and issues and get feedback from the core developers.


## The public pitch
*This will be shown in the Language Summit schedule on the conference website and published ahead of the event. Write one or two short paragraphs to pitch this topic to the attendees. This is your chance to encourage people to discuss the topic with you!*

Python's continuing evolution to a multi-threaded language stresses the need for safe sharing of data. The ability to construct immutable object graphs permits such safe sharing, gives strong guarantees against unintended modifications, simplifies correctness, security, and opens up for optimisations of memory management, object layout, etc.

While immutable data is very useful on its own, it forms the basis of several extensions including support for sharing immutable data between subinterpreters and threads (with and without GIL), and clever ways to manage immutable cyclic data structures just using reference counting.

