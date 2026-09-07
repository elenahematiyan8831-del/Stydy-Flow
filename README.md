# StudyFlow

#### Video Demo:
https://youtu.be/YhAiPjhLNLQ

#### Description:

StudyFlow is a web-based study and task management application designed to help students organize their academic work, manage assignments, and monitor their progress. I created this project because students often have many different subjects and tasks to manage, and a simple task list does not always make it easy to decide what should be done first.

The application starts with a registration and login system. Users can create their own account and securely log in using a hashed password. Each user's subjects and tasks are associated with their account, so users can manage their own study information.

After logging in, the user reaches the dashboard. The dashboard displays the total number of tasks, the number of completed tasks, and an overall progress percentage. It also shows the user's current tasks and provides quick access to creating new tasks.

The Subjects section allows users to create subjects such as Mathematics, C#, Web Design, or English. Subjects can then be assigned to individual tasks. The application also displays the number of tasks associated with each subject.

The Tasks section is the main part of StudyFlow. Users can create tasks with a title, description, subject, due date, and priority. Priority can be High, Medium, or Low. Users can edit existing tasks, mark tasks as completed, undo completion, or delete tasks. The task list can also be filtered by priority and completion status. Tasks can be sorted by due date, priority, title, or creation order.

StudyFlow also includes a Smart Planner. The planner displays unfinished tasks and automatically organizes them according to their priority and due date. High-priority tasks appear before lower-priority tasks, making it easier for the user to decide what should be studied first.

Another important feature is the Statistics page. It displays the total number of tasks, completed tasks, pending tasks, high-priority tasks, and overall completion percentage. It also provides progress information for individual subjects. This allows users to see their study progress instead of only viewing a list of assignments.

The project uses Flask for the backend and SQLite for data storage. Flask was chosen because it provides a simple structure for building a web application with Python. SQLite was selected because it is lightweight and does not require a separate database server. SQL queries use parameters when receiving user-controlled values.

The main application logic is contained in `app.py`. It includes authentication, subject management, task management, filtering, sorting, the Smart Planner, and statistics. `helpers.py` contains the `login_required` function used to protect pages that require authentication. `schema.sql` describes the database tables. The HTML templates are stored in the `templates` directory, while the custom CSS and JavaScript files are stored in the `static` directory.

The visual design uses a light blue and white color scheme. I chose this design because I wanted StudyFlow to feel clean, calm, and suitable for studying. Bootstrap is used for responsive layout components, while custom CSS provides the application's visual identity.

During development, AI tools were used as an assistance resource for implementation and debugging. The generated suggestions were reviewed, tested, modified, and integrated by the project author.
