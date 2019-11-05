.. _philosophy:

DebOps philosophy
=================

In this section, you can read about DebOps from a personal perspective of its
authors. We hope that this will help explain how the project came to be, what
its goals are, and where it is heading.


Maciej Delmanowski
------------------

I'm using GNU/Linux as operating system since 2001. Since 2002 I'm using primarily
the `Debian GNU/Linux <https://www.debian.org/>`__ distribution, or its
derivatives, both on private and work computers, workstations and servers
alike. I really like Debian, both from the software side, as well as the
`philosophy behind the project <https://wiki.debian.org/WhyDebian>`_.

At the moment I'm not a Debian Developer, however I would still like to
contribute to the project, at least in a small, but meaningful way. Most of my
professional focus for the last few years has been on Debian system
administration, therefore this is what I'd like to offer to the Debian
community - my experience as a sysadmin, the knowledge how to manage a Debian
host, or a cluster of hosts together.

In the past that was primarily done through `books <https://debian-handbook.info/>`_,
blog posts, HOWTOs, manual pages. But this method is brittle, and requires
a person that can process the information, adapt it to their needs as well as
changes to the current operating system and software stack, and perform the
necessary operations. Recently, multiple configuration management tools have
been created, that offer another avenue of sharing the knowledge about system
administration in a different, programmable and automated way.

The `Ansible <https://github.com/ansible/ansible>`__ project is one such tool.
It is very easy to use, but powerful configuration language, very friendly
towards system administrators. In the past, while evaluating different
configuration management systems to use at my workplace, I noticed that there
were no easy to use, extensible, general purpose projects that managed
Debian-based environments using Ansible. Since I needed such a project to
manage different, heterogeneous Debian servers, I started writing one. Over
time, it has evolved into DebOps.

The name "DebOps" is a portmanteau of "Debian" and "Operations", and it hints
at the purpose of the project itself - to help `IT Operations <https://en.wikipedia.org/wiki/Information_technology_operations>`__
teams manage Debian or Debian-based environments. I don't think that I can be
cited as an author of this name. Instead, I'd like to quote an article written
by Enrico Zini, a Debian Developer, who in 2014 wrote about "Debops"
methodology:

    What I like the most about being a Developer is building tools to (hopefully)
    make someone's life better. I like it when my software gets used, and people
    thank me for it, because there was a need they had that wasn't met before, and
    thanks to my software now it is being met. I am maintaining software for
    meteorological research that is soon going to be 10 years old, and is still
    evolving and getting Real Work done.

    I like to develop software as if it is going to become a part of human cultural
    heritage, developing beyond my capacity, eventually surviving me, allowing
    society to declare that the need, small as it was, is now met, and move on to
    worry about some other problem. I feel that if I'm not thinking of my software
    in that way, then I am not being serious. Then I am not developing something
    fit for other people to use and rely on.

    This involves Development as much as it involves Operations: tracking security
    updates for all the components that make up a system. Testing. Quality
    assurance. Scalability. Stability. Hardening. Monitoring. Maintenance
    requirements. Deployment and upgrade workflows. Security. I came to learn that
    the requirements put forward by sysadmins are to be taken seriously, because
    they are the ones whose phone will ring in the middle of the night when your
    software breaks.

    I am also involved in more than one software project. I am responsible for
    about a dozen web applications deployed out there in the wild, and possibly
    another dozen of non-web projects, from terabyte-sized specialised archival
    tools to little utilities that are essential links in someone's complex
    toolchain.

    I build my software targeting Debian Stable + Backports. At FOSDEM I noticed
    that some people consider it uncool. I was perplexed.

    It provides me with a vast and reasonably recent set of parts to use to build
    my systems. It provides me with a single bug tracking system for all of them,
    and tools to track known issues in the systems I deployed. It provides me with
    a stable platform, with a well documented upgrade path to the next version. It
    gives me a release rhythm that allows me to enjoy the sweet hum of spinning
    fans thinking about my next mischief, instead of spending my waking time
    chasing configuration file changes and API changes deep down in my dependency
    chain.

    It allows me to rely on Debian for security updates, so I don't have to
    track upstream activity for each one of the building blocks of the systems I
    deploy. It allows me not to worry about a lot of obscure domain specific
    integration issues. Coinstallability of libraries with different ABI versions.
    Flawless support for different versions of Python, or Lua, or for different
    versions of C++ compilers.

    It has often happened to me to hear someone rant about a frustrating situation,
    wonder how come it had never happened to me, and realise that someone in
    Debian, who happens to be more expert than I can possibly be, had thought hard
    about how to deal with that issue, years before. I know I cannot be an expert
    of the entire stack from bare iron all the way up, and I have learnt to stand
    on the shoulders of giants.

    'Devops' makes sense for me in that it hints at this cooperation between
    developers and operators, having constructive communication, knowing that each
    side has their own needs, trying their best to meet them all. It hints at a
    perfect world where developers and operators finally come to understand and
    trust each other's judgement. I don't know that perfect world, but I, a
    developer, do like to try to understand and trust the judgement of sysadmins. I
    sympathise with my sysadmin friends who feel that devops is turning into a
    trend of developers thinking they can do without sysadmins. Reinventing package
    managers. Bundling dependencies. Building "apps" instead of components.

    I wish that people who deploy a system built on such premises, have it become
    so successful that they end up being paid to maintain them for their whole
    career. That is certainly what I wish and strive for, for me and my own
    projects. In my experience, a sustainable and maintainable system won't come
    out of the startup mindset of building something quick&dirty, then sell it and
    move on to something else.

    In my experience, the basis for having sustainable and maintainable systems
    have been well known and tested in Debian, and several other distributions, for
    over two decades. At FOSDEM, we thought that we need a name for such a mindset.

    Between beers, that name came to be "debops". (It's not just Debian, though:
    many other distributions get it right, too)

    -- Enrico Zini, `"Debops" <https://www.enricozini.org/blog/2014/debian/debops/>`_

His words deeply resonated with me. I would like to think that my work on
DebOps will be useful to other Debian sysadmins and users out there, for many
years to come. I hope that with time DebOps will grow beyond just a software
project and will become something much more, either within Debian itself, or
right beside it.


Robin `ypid` Schneider
----------------------

I made the switch to GNU/Linux as my main OS in August 2009 and self-taught
myself most of it‘s internals when I was in the last years of secondary school.
Since 2012 I'm primarily using `Debian GNU/Linux <https://www.debian.org/>`__
on private and work computers and servers alike.
I really like Debian and would like to become a Debian Developer some day.

Starting in 2012, I worked 5 years as a IT Consultant until 2017, mainly
deploying and advocating Free and Open Source software. During that time, I
set up and deployed a monitoring appliance based on Debian, Icinga and Check_MK
as well as file syncing appliance based on Debian and ownCloud. The file syncing
appliance was build from the ground up with DebOps and deployment was also done
with Ansible and DebOps. The monitoring appliance was set up by me before I knew
fancy tools like Ansible/DebOps. Currently, I am working as a full-time
sysadmin, mainly doing scripting, monitoring, security and automation. Sadly, neither
Debian, nor Ansible/DebOps play a big role currently. Feel free to get in touch if
you think otherwise and are fully committed to Free Software.

I came to DebOps shortly after I settled on Ansible as the configuration
management system of choice for my private infrastructure, because DebOps is the
most comprehensive approach to CM for Debian GNU/Linux I could find. Since
2015-02 I am using it for most of my machines and various projects at work and
I'm quite happy with it. I did not lose much time as a user of DebOps and
started contributing to it and helping DebOps evolve. In 2016-07, I officially
became the second DebOps Developer when Maciej and me set up the :ref:`debops.keyring`.

One of my big interests is IT security, so together with Maciej I put a lot of
effort into DebOps to create something worthwhile, that can be relied upon to a
reasonable extend, be Free Software and auditable. I am actively working on making the
project as secure and privacy-friendly by default as possible and I will not
stand backdoors or any kind of weakening which third parties might like to
include in projects like DebOps. I am not using every component/role that
DebOps provides currently, but the ones I do are carefully reviewed and
tested by me. Refer to https://github.com/ypid/ypid-ansible-common/ for my
ongoing, digitally signed status of this review. I understand that being a
developer of a project designed to set up and configure thousands of servers and
workstations (not the main goal of DebOps but it works quite nice for me)
results in a lot of responsibility. I am doing what I can to keep up with that.
For example, I switched to Qubes OS in 2016-12. All my development work is done
from there from now on. OpenPGP signatures come from stripped down, offline
VMs. The reason I am doing all of this as a responsable sysadmin and developer
is to keep our dear users safe during those difficult and advanced times.

DebOps is already one of a kind when it comes to configuration management for
Debian. The reason I joined the project is it’s commitment to excellence which
I now like to give back to the project and all its users.

"We do these things not because they are easy but because they are hard."
