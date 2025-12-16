# Learning-MLOps

This repository acts as a hands-on tutorial on **MLOps** based on the AIO course material.

## Continuous Integration and Continuous Delivery (CI/CD)

### The problem: "It works on my machine"

In reality, after developing new code or a newly trained model, the developer will have to `git push` and perform several practices:
- SSH into a staging or production server
- `git pull` the latest changes
- Install dependencies on that server
- Run test suite
- Try to inference the model
- Build a new docker image
- Push that image to a container registry like `Dockerhub`
- Finally, pull the new image on the server and restart the application

<!-- <p align="center">
  ![Problem](Images/Problem.jpg)
</p> -->

The problem is, the code can run perfectly in the local/development environment. However, when it comes to staging or production, it might break because of manual errors, inconsistent environment configurations (dependency versions, runtime differences), etc. This deployment step is a long, manual, and error-prone process.

Therefore, in this repository, I will try to use **CI/CD with Github Actions, Jenkins (ngrok + Github Webhook) and Docker (Dockerhub)** to address the flaws mentioned above, trying to build a fully automated pipeline for a simple ML Web Application.

### Implementation

The mock project is simply an Iris flower classifier built with Scikit-learn, served via a REST API using FastAPI.

#### Step 1: Building the Mock Project

```bash
iris-cicd-project/
├── .github/
│   └── workflows/
│       └── cicd.yml          # GitHub Actions workflow definition
├── src/
│   ├── __init__.py
│   ├── app.py                # FastAPI application logic
│   └── train_model.py        # Script for training the ML model
├── tests/
│   ├── __init__.py
│   ├── test_app.py           # Pytest for the FastAPI API endpoints
│   └── test_model.py         # Pytest for the model training and logic
├── Dockerfile                # Recipe for building the application container
├── Jenkinsfile               # Jenkins pipeline-as-code definition
├── requirements.txt          # List of Python dependencies (e.g., fastapi, scikit-learn)
└── .gitignore                # Files and folders to ignore (e.g., __pycache__, venv/)
```

#### Step 2: Containerizing with Docker

We will create a `Dockerfile` for dependency version consistency (To be able to use the same environment on different machines):

1.  Start `FROM` a base Python image.
2.  `COPY` the `requirements.txt` file and `RUN pip install` to get dependencies.
3.  `COPY` the rest of the application code.
4.  `RUN` the `train_model.py` script. The model is trained and saved inside the image during the build process.
5.  `CMD` specifies the command to run the FastAPI server when the container starts.

#### Step 3: Automation with Jenkins

Jenkins is an automation server. We will create a `Jenkinsfile`, which define the entire deployment process in a file and version-control:

1.  **Checkout:** Pull the latest code from GitHub (We will need to setup ngrok using `ngrok http 8080` and configuring `Github Webhook` for this).
2.  **Setup Python Environment:** Create a clean virtual environment and install dependencies. This prevents any pollution between builds.
3.  **Train Model:** Run the training script.
4.  **Test Model & API:** This is our quality gate. It runs `pytest` on both our model and API tests. If any test fails, the pipeline stops immediately.
5.  **Build Docker Image:** Execute the `docker build` command.
6.  **Push to Docker Hub:** Log in to Docker Hub (using credentials securely stored in Jenkins) and push the newly built image.
7.  **Cleanup:** Remove the Docker image from the Jenkins server to save space.

Then, we will need to create a `docker-compose.yml` file to build a container for this Jenkins server to run on.

Now, every `git push` automatically triggered this entire sequence.

<!-- <p align="center">
  ![Jenkins](Images/Jenkins.jpg)
</p> -->

#### Step 3: Alternative - GitHub Actions

Alternatively, I implemented the same logic using GitHub Actions. Now, instead of a separate server, the automation runs directly within GitHub, triggered by events in the repository.

The configuration lives in a YAML file under `.github/workflows/`. The logic was very similar to the Jenkins pipeline, but the syntax felt more modern.

Key parts of the workflow file:

*   **`on: [push]`:** Defines the trigger—run this pipeline on every push to the `main` or `develop` branches.
*   **`jobs:`:** I defined one main job called `build-and-deploy`.
*   **`steps:`:** This is where the magic happens. Instead of writing shell commands for everything, I could leverage pre-built "actions" from the GitHub Marketplace.
    *   `actions/checkout@v4`: To check out the code.
    *   `actions/setup-python@v5`: To set up the correct Python version.
    *   `docker/login-action@v3`: To securely log in to Docker Hub.
    *   `docker/build-push-action@v5`: To build and push the image in a single, optimized step.

I stored my Docker Hub username and access token as encrypted "Secrets" in my GitHub repository settings, which the workflow could access securely.
