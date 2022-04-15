########
Examples
########

Below are some simple examples of using ``Batches`` tasks. Note that they the
eamples do not fully configure the :class:`~celery.Celery` instance, which depends
on your setup (e.g. which broker/backend you're planning to use).

Simple Example
##############

A click counter that flushes the buffer every 100 messages, and every
10 seconds.  Does not do anything with the data, but can easily be modified
to store it in a database.

.. literalinclude:: examples/counter.py
    :language: python

Then you can ask for a click to be counted by doing::

    >>> count_click.delay(url='http://example.com')

Database example
################

It can be useful to batch together tasks to reduce database updates (in situations
where a missed update is not important), e.g. updating the last seen time of a user:

.. literalinclude:: examples/last_seen.py
    :language: python

Bulk inserting/updating data
############################

It can also be useful to just bulk insert data as quickly as possible, but when the discrete data is from separate tasks.

.. literalinclude:: examples/bulk_insert.py
    :language: python

Example returning results
#########################

An interface to the GitHub API that avoids requesting the API endpoint for each
task. It flushes the buffer every 100 messages, and every 10 seconds.

.. literalinclude:: examples/github_api.py
    :language: python

Using the API is done as follows::

    >>> result = check_emoji.delay('celery')
    >>> assert result.get() is False
