"""
The meat.

Things to do:
    TaskFinder
     - querys a (file|db) for what sort of tasks to run
    Task
     - initialize from task data pulled by TaskFinder
     - enumerate the combination of args and kwargs to sent to this task
     - provide a function which takes *args and **kwargs to execute the task
     - specify the type of schedule to be used for this task
    ScopeFinder
     - querys a (file|db) for the set of parameter combinations to send to the task
    Scheduler
     - initialize from schedule data pulled by ScheduleFinder
     - determine if a task and arguement combination should run
    Registry
     - manage the state of all jobs in progress
"""
