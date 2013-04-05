.. momonitor documentation master file, created by
   sphinx-quickstart on Sat Mar 23 21:56:27 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

MoMonitor : Monitoring for Developers
=====================================

Release v 0.1

System monitoring shouldn't be scary. MoMonitor is here to help. 

MoMonitor is a simple `Apache2 License <http://www.apache.org/licenses/LICENSE-2.0.html>`_ monitoring solution built by developers, for developers. It was created out of frustration of configuring and maintaining `Nagios <http://www.nagios.org/>`_.

Why MoMonitor?
--------------

* | **Manage your checks via a simple WebUI**
  | Edit, create, and delete system checks with a simple WebUI! No more needing to update foreign configuration files to manage your checks.
* | **Designed for extensibility**
  | Adding new types of health checks is easy as cake. Just create a new django model, and you're good!
* | **Know what, when, and why**
  | Know when your checks run, whether they succeeded or failed, and why! MoMonitor gives you an intuitive, human-readable interface for doing so.
* | **Alert via** `Pagerduty <http://www.pagerduty.com/>`_ **or generic email**
  | We have implemented builtin support for PagerDuty. Alerts are sent out immediently upon a failed check.
* | **Actively being worked on at** `MoPub <http://mopub.com>`_
  | MoPub uses MoMonitor as its centralized monitoring system. We monitor a system that handles over a billion requests everyday.

How it works
============

MoMonitor is a simple django app that manages and runs health checks on your systems. If a health check fails, MoMonitor will alert you immedietely.

As a developer, you define services and health checks. Services are collections of health checks that share a bunch of defaults (i.e. check frequency, alert type). Several types of health checks have been implemented to help you monitor every aspect of your system.



See the `video tutorial <http://www.youtube.com/watch?v=uL5ddl5wpac>`_ for a brief overview of the momonitor WebUI.

We also put together a quick `presentation <http://mopub.github.com/momonitor/slideshow>`_ to highlight the goals of momonitor.

Want to start creating checks right away? See the `demo video <http://youtu.be/YVNQo98Nrio>`_ about creating checks

Screenshots
-----------

.. image:: img/momonitor-1.jpg
   :height: 100px
   :width: 125px
   :target: img/momonitor-1.jpg

.. image:: img/momonitor-2.jpg
   :height: 100px
   :width: 125px
   :target: img/momonitor-2.jpg

.. image:: img/momonitor-3.jpg
   :height: 100px
   :width: 125px
   :target: img/momonitor-3.jpg

.. image:: img/momonitor-4.jpg
   :height: 100px
   :width: 125px
   :target: img/momonitor-4.jpg

.. image:: img/momonitor-5.jpg
   :height: 100px
   :width: 125px
   :target: img/momonitor-5.jpg

.. image:: img/momonitor-7.jpg
   :height: 100px
   :width: 125px
   :target: img/momonitor-7.jpg

.. image:: img/momonitor-8.jpg
   :height: 100px
   :width: 125px
   :target: img/momonitor-8.jpg

Getting Started
===============

Requirements
------------

* | **PostgreSQL**
  | MoMonitor has only been tested with PostgreSQL, however there isn't any reason why it shouldn't work with any Django supported backend. (i.e. MySQL, SQLite)
* | **Python** 
  | MoMonitor has been tested with Python2.7. Install the requirements included in the requirements file (pip install -r requirements.txt)
* | **Redis**
  | MoMonitor keeps check state in a redis cache. Note that check state is currently not persisent unless you have enabled Redis persistence. This is optional.
* | **Cron**
  | MoMonitor depends on Cron to run the management script.

::

     python manage.py service_check_cron
      
* | **Google OAuth**
  | MoMonitor currently uses OAuth tied with your google account. A more generic authentication method will be implemented in future versions.
  | You need to set the domain white list to the email address that you use with your gmail account. For example, since we have @mopub.com for MoPub, we use the following configuration:

::

    GOOGLE_WHITE_LISTED_DOMAINS = ['mopub.com']


Setup from Nothing
------------------

First clone the Repo:
::

    git clone git@github.com:mopub/momonitor.git

Next, you will need to setup your database and sync your Django Models. Make sure the database is already running.
::

    psql -U postgres -c "CREATE ROLE <role-name> with password '<password>' WITH LOGIN;"
    psql -U postgres -c "CREATE DATABASE <database-name> with owner <role-name>;"
    python manage.py syncdb
    python manage.py migrate

Update Section 2 of the settings.py file with your database configurations
::

    DATABASES = {
       'default': {
          'ENGINE': 'django.db.backends.postgresql_psycopg2',
          'NAME': '<database-name>',
          'USER': '<role-name>',
          'PASSWORD': '<password>',
          'HOST': 'localhost',
          'PORT': '5432',
      }
  }

(optional) Set Variables required for certain types of checks
::

      UMPIRE_ENDPOINT = ""
      SENSU_API_ENDPOINT = ""
      GRAPHITE_ENDPOINT = ""

      #OAuth rule. Only allow people with a google email ending in 'example.org' to access the site   
      GOOGLE_WHITE_LISTED_DOMAINS = ['gmail.com']

      # Set this to the Domain of the site that will be hosting momonitor   
      DOMAIN = "http://localhost"
      
      #By default, all checks are enabled. Select only a few checks by defining this variable
      CHECK_MODELS=[]

Start the server
::

   python manage.py runserver

Configure Cron to Run. Cron should **run the service_check_cron every minute** to keep MoMonitor up to date. While this is not the most efficient way to keep checks runnning, it has worked for MoPub so far.

**/etc/cron.d/mycron**

::

   * * * * * <user> python <path-to-repo>/momonitor/manage.py service_check_cron

And, you're ready to go!


Overview
========

What it is
----------

MoMonitor is a Django app that runs on a PostgreSQL backend and Redis Cache. Check and service configurations are kept in Postgres while application state is kept in Redis. MoMonitor is configured to use Google OAuth for authentication via django-social-auth. MoMonitor relies on cron to run checks.

Essentially two types of objects exist in MoMonitor: services and service checks. Service checks that test like parts of your infrastructure are grouped into single service. Services provide defaults and alerts for the checks they contain. 

Types of Checks
---------------

One of the great advantages of MoMonitor is the ability to easily define new types of checks. At MoPub, we have already defined several types of checks:

* | **Simple Check** 
  | checks a single HTTP endpoint and reports whether the HTTP response returned with a 200 or non-200 status code.
* | **Umpire Check** 
  | implements the Umpire API to report on graphite data. Umpire checks require an `Umpire <https://github.com/heroku/umpire>`_ Server and `Graphite <http://graphite.wikidot.com/>`_ Server. To integrate with MoMonitor you need to add the follwing settings constants with the URL endpoints of your servers...

::

   UMPIRE_ENDPOINT = "http://example.org/check"
   GRAPHITE_ENDPOINT = "http://example.org"

* | **Compare Check** 
  | hits an HTTP endpoint that returns serialized data in the response body (i.e. json). Specify a field in the serialized data using dot notation, and compare the value of that field to a value that your specify.
* | **Code Check** 
  | runs code (that you upload) on the momonitor server. Currently only Python is supported.
* | **Sensu Check** 
  | implements the Sensu Aggregate API and alerts when any servers fail a sensu check.
  | Sensu checks require a `Sensu <https://github.com/sensu/sensu>`_ Server. To integrate with MoMonitor...
* | **Graphite Check**
  | Emulates the function of Umpire. Apply a minimum and maximum threshold on a graphite metric, and get alerted when the value goes beyond those thresholds.

::

    SENSU_API_ENDPOINT = "http://example.org:4567"

Extra Check Options
-------------------

* | **Frequency** 
  | Cron-like interface to specify how often you would like your check to run
* | **Failures before alert** 
  | Number of consecutive failures to occur before an alert is sent
* | **Silenced** 
  | If a check is silenced, it will not send alerts even if it is failing

Check Statuses
--------------

* | **Good** 
  | The last check was passing
* | **Bad** 
  | The check has failed at least X times (default 1). This value is configurable via the "Failures Before Alert" option
* | **Unknown** 
  | The service / endpoint providing the check either failed or gave a non-valid response

Types of Alerts
---------------

* | **Email** 
  | Email alerts will send an an email to the specified contact upon a check failing
* | **Pagerduty** 
  | Pagerduty alerts will trigger an event to the specified Pagerduty service key upon a check failing
* | **None** 
  | This option will disable alerts for the service


Other Features
==============

MoMonitor comes with a couple additional features that make it more fun. These are by no means neccessary, but they continue to help us at MoPub

* | **Mobile UI** 
  | On the go? Enable the momonitor/mobile django app to get access to MoMonitor's mobile interface. Currently, the interface allows you to view the health of all checks and silence them if neccessary.
* | **Slideshow** 
  | Have an extra unused TV hanging on the wall? Enable the momonitor/slideshow django app to get access to MoMonitor's slideshow feature. Based on all of the checks you add, MoMonitor will automatically create a slideshow for each service, which cycles through graphs of all of your checks.  

Testing
=======

For testing, we are using Django's builtin unittest.TestCase and a custom-made Flask http server to mimic external services (like Sensu and Umpire). To run tests, you must start up the flask server before running the test command:

::

    $ python manage.py start_testing_faux_server

And then, in a separate tab...
::

    $ python manage.py test main
    $ python manage.py test mobile

Feedback
========

We love feedback. If you have any questions about the momonitoring system, contact Rob at rob@mopub.com

Found an issue? We'd greatly appreciate it you `told us <https://github.com/mopub/momonitor/issues>`_ !


