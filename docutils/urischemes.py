"""
`schemes` is a dictionary with lowercase URI addressing schemes as
keys and descriptions as values. It was compiled from the index at
http://www.w3.org/Addressing/schemes.html (revised 2001-08-20).
"""

# Many values are blank and should be filled in with useful descriptions.

schemes = {
      'about': 'provides information on Navigator',
      'acap': 'Application Configuration Access Protocol',
      'addbook': "To add vCard entries to Communicator's Address Book",
      'afp': 'Apple Filing Protocol',
      'afs': 'Andrew File System global file names',
      'aim': 'AOL Instant Messenger',
      'callto': 'for NetMeeting links',
      'castanet': 'Castanet Tuner URLs for Netcaster',
      'chttp': 'cached HTTP supported by RealPlayer',
      'cid': 'content identifier',
      'data': ('allows inclusion of small data items as "immediate" data; '
               'RFC 2397'),
      'dav': 'Distributed Authoring and Versioning Protocol; RFC 2518',
      'dns': 'Domain Name System resources',
      'eid': ('External ID; non-URL data; general escape mechanism to allow '
              'access to information for applications that are too '
              'specialized to justify their own schemes'),
      'fax': ('a connection to a terminal that can handle telefaxes '
              '(facsimiles); RFC 2806'),
      'file': 'Host-specific file names',
      'finger': '',
      'freenet': '',
      'ftp': 'File Transfer Protocol',
      'gopher': 'The Gopher Protocol',
      'gsm-sms': ('Global System for Mobile Communications Short Message '
                  'Service'),
      'h323': 'video (audiovisual) communication on local area networks',
      'h324': ('video and audio communications over low bitrate connections '
               'such as POTS modem connections'),
      'hdl': 'CNRI handle system',
      'hnews': 'an HTTP-tunneling variant of the NNTP news protocol',
      'http': 'Hypertext Transfer Protocol',
      'https': 'HTTP over SSL',
      'iioploc': 'Internet Inter-ORB Protocol Location?',
      'ilu': 'Inter-Language Unification',
      'imap': 'Internet Message Access Protocol',
      'ior': 'CORBA interoperable object reference',
      'ipp': 'Internet Printing Protocol',
      'irc': 'Internet Relay Chat',
      'jar': 'Java archive',
      'javascript': ('JavaScript code; evaluates the expression after the '
                     'colon'),
      'jdbc': '',
      'ldap': 'Lightweight Directory Access Protocol',
      'lifn': '',
      'livescript': '',
      'lrq': '',
      'mailbox': 'Mail folder access',
      'mailserver': 'Access to data available from mail servers',
      'mailto': 'Electronic mail address',
      'md5': '',
      'mid': 'message identifier',
      'mocha': '',
      'modem': ('a connection to a terminal that can handle incoming data '
                'calls; RFC 2806'),
      'news': 'USENET news',
      'nfs': 'Network File System protocol',
      'nntp': 'USENET news using NNTP access',
      'opaquelocktoken': '',
      'phone': '',
      'pop': 'Post Office Protocol',
      'pop3': 'Post Office Protocol v3',
      'printer': '',
      'prospero': 'Prospero Directory Service',
      'res': '',
      'rtsp': 'real time streaming protocol',
      'rvp': '',
      'rwhois': '',
      'rx': 'Remote Execution',
      'sdp': '',
      'service': 'service location',
      'shttp': 'secure hypertext transfer protocol',
      'sip': 'Session Initiation Protocol',
      'smb': '',
      'snews': 'For NNTP postings via SSL',
      't120': 'real time data conferencing (audiographics)',
      'tcp': '',
      'tel': ('a connection to a terminal that handles normal voice '
              'telephone calls, a voice mailbox or another voice messaging '
              'system or a service that can be operated using DTMF tones; '
              'RFC 2806.'),
      'telephone': 'telephone',
      'telnet': 'Reference to interactive sessions',
      'tip': 'Transaction Internet Protocol',
      'tn3270': 'Interactive 3270 emulation sessions',
      'tv': '',
      'urn': 'Uniform Resource Name',
      'uuid': '',
      'vemmi': 'versatile multimedia interface',
      'videotex': '',
      'view-source': 'displays HTML code that was generated with JavaScript',
      'wais': 'Wide Area Information Servers',
      'whodp': '',
      'whois++': 'Distributed directory service.',
      'z39.50r': 'Z39.50 Retrieval',
      'z39.50s': 'Z39.50 Session',}
