# Study Planner

An intelligent, AI-powered study assistant designed to optimize your academic schedule. This application shifts the burden of planning from your shoulders to an algorithm, ensuring you maximize your study efficiency without the burnout.

## Core Features

- **Dynamic Task Management:** Track complex projects with integrated deadline, subject, and difficulty weighting.
- **Smart Scheduling:** AI-assisted optimization that mathematically balances urgency, remaining workload, and cognitive load.
- **Availability Mapping:** A flexible, user-centric interface that adapts to your daily time constraints.
- **Secure Authentication:** Built-in OAuth support (Google) for secure, cross-device access.

## The Logic: Why It Works

The Study Planner doesn't just list tasks—it solves a multi-variable optimization problem. Here is how we prioritize your success:

- **Adaptive Urgency Weighting:** As deadlines approach, tasks receive a priority boost. The closer you get to a due date, the more the algorithm forces that task to the front of your queue.
- **Cognitive Load Balancing:** We factor in "difficulty" and "subject fatigue." By strategically rotating subjects, we help you avoid cognitive plateaus and maintain peak focus.
- **Dynamic Workload Distribution:** The algorithm continuously monitors your progress. If a task has been neglected or is lagging behind, the scheduler automatically reallocates time in your upcoming sessions to keep you on track.

*Note: Our proprietary weighting system uses a multi-factor scoring model to ensure your schedule remains balanced. These weights are currently in iterative testing to find the optimal harmony between academic intensity and sustainable progress.*

## Architecture & Reliability

- **High-Integrity Data Layer:** We use self-validating models (`__post_init__` data checking) to ensure your schedule is mathematically sound, preventing data corruption before it reaches the database.
- **Decoupled Business Logic:** By strictly separating our UI from our scheduling service and database repository, we ensure the system is maintainable, scalable, and easy to audit as our algorithms evolve.
- **Robust State Management:** Our centralized authentication and session orchestration ensure that your study progress is saved, synced, and secure.

## Upcoming Roadmap
- [ ] **Calendar Integration:** One-click export to Google/Outlook/Apple Calendar.
