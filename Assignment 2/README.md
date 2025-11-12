☁️ CloudConnect - Cloud Resource Manager
This is a a modular, extensible, and robust cloud management simulator, built in Python. It serves as a practical demonstration of core Object-Oriented Programming (OOP) principles and SOLID design, using powerful design patterns to solve common software engineering problems.

The system allows a user to create, start, stop, and delete various "cloud" resources like AppService and StorageAccount through a menu-driven CLI.

🚀 Core Design Decisions
This project was built from the ground up to be a showcase of SOLID design. Every requirement from the prompt was mapped to a specific design pattern or principle.

1. Project Structure (Single Responsibility Principle)

The project is broken into a modular file structure. Each class and module has a single, well-defined responsibility:

CloudManager: Manages user interaction and orchestration. It delegates all work.

ResourceFactory: Only responsible for creating resources.

CloudResource: The abstract "Context" that holds data and delegates behavior.

patterns/state.py: All lifecycle and state transition logic (and only that logic) lives here.

logging/observers.py: All logging implementation (and only that) lives here.

2. The "Big Three" Design Patterns

🏭 The Factory Pattern (Open/Closed Principle)

Requirement: "Extending CloudConnect... plug in without changing existing code. Use a registry mechanism."

Implementation: The ResourceFactory class maintains a _registry (a dictionary).

SOLID (Open/Closed): This pattern is the key to the Open/Closed Principle. The CloudManager is closed for modification—it never needs to know what an AppService is. The system is open for extension:

Create a new resources/database.py file with a Database class.

Add ResourceFactory.register_resource("Database", Database) at the bottom of that file.

Add from . import database in resources/__init__.py.

That's it. The CloudManager's "Create Resource" menu will automatically show "Database" as an option.

⚙️ The State Pattern (Single Responsibility & Open/Closed)

Requirement: "Lifecycle Behavior... Invalid operations... should be handled gracefully."

Implementation: We use the ResourceState interface (CreatedState, StartedState, etc.). The CloudResource (the "Context") holds an instance of a state and delegates all lifecycle calls (like start()) to it.

SOLID (Single Responsibility): This is a perfect example of the SRP. The AppService class has no idea how to start, stop, or what to do if delete() is called while it's running. All of that complex if/else logic is moved into the state classes, each responsible for one state.

How it works: When a resource is in StartedState, its start() method simply notifies "already running" and returns self (no state change). When it's in StoppedState, its start() method notifies "restarted" and returns a new StartedState().

📊 The Observer Pattern (Dependency Inversion Principle)

Requirement: "Activity Logging... must be attachable without changing resource logic."

Implementation: The CloudResource is the "Observable." It maintains a list of Observer objects. The ConsoleLogger and FileLogger are "Observers." When a resource's state changes, it calls notify(), which loops through its observers and calls their update() method.

SOLID (Dependency Inversion): This is a classic example of DIP. The CloudResource (a high-level module) does not depend on the FileLogger (a low-level module). Both depend on an abstraction (the Observer interface). This "loose coupling" means we could add a SlackLogger or EmailLogger without ever touching the CloudResource code.

3. Dependency Injection (Solving the "Create" Log Problem)

Problem: How do you log a resource's "Created" event, if the loggers are attached after it's created?

Solution (Dependency Injection): We "inject" the dependencies at creation time.

The CloudManager (the main app) owns the ConsoleLogger and FileLogger instances.

When a user creates a resource, the CloudManager passes this list of loggers to the ResourceFactory.

The ResourceFactory passes this list to the CloudResource's constructor.

The last thing the CloudResource constructor does is call notify("Created", ...).

Benefit: The resource is "born" with its loggers, allowing it to log its own birth. This follows DIP by having the dependencies provided from the outside.

📜 Assumptions
Soft Deletion: "Deleting" a resource moves it to a DeletedState. It is not removed from the CloudManager's memory. This is for record-keeping, allowing the user to see that a resource was deleted.

Log File: The FileLogger appends all logs from all resources to a single cloud_logs/cloudconnect.log file for simplicity.

Basic Validation: The CLI helpers perform basic validation (e.g., checking for menu numbers) but not exhaustive validation (e.g., resource name formats).

🚀 How to Run
Ensure you have Python 3.7+ installed.

Place all the files in the directory structure shown above.

Run the main application:

Bash
python main.py
Follow the on-screen menu. A cloud_logs directory will be created in the same folder.