# WreckIT Attack-Defense CTF Backend

This is the backend software for an Attack-Defense Capture The Flag (CTF) competition used in **Wrect IT 5.0**.

## Features
- Facilitates real-time Attack-Defense CTF matches
- Handles flag submission, team scoring, and game state
- Includes basic user management and team handling

## Known Issues
- **Bugs**: Some functionalities may not work as expected.
- **Efficiency**: The current implementation is not optimized, leading to performance bottlenecks.
- **Caching**: Caching mechanisms need improvement for smoother performance.

We welcome **forks** and **merge requests** to help improve the project!

## Installation

### 1. Using Local Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/rafliher/wreckitattdef-server.git
   cd wreckitattdef-server
   ```

2. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```

3. Initialize the database by running the following command **twice**:
   ```bash
   python init_db.py
   ```

4. Run the server:
   ```bash
   python run.py
   ```

### 2. Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/rafliher/wreckitattdef-server.git
   cd wreckitattdef-server
   ```

2. Build and run the application using `docker-compose`:
   ```bash
   docker-compose up --build
   ```

## Contributions

This project is open for improvements. Feel free to:
- **Fork** the repository
- Submit **pull requests** with bug fixes or performance improvements

## License
This project is licensed under the [MIT License](LICENSE).

---

### Contact
Developed by Herlambang Rafli Wicaksono  
For any questions, feel free to reach out: raflihw1@gmail.com
