# RiverScope

A website to display river levels and level trends across all gauging stations in the UK, and provide customisable alerts on river levels. It will be useful for anyone using rivers for business or recreation, such as kayakers looking for high, fast water, pleasure boat owners who may need to adjust mooring lines, anglers looking for slow water and people with flood concerns.

## Requirements

This application is built using Django and Python 3

## Installation

.. code:: bash

    # Clone the repository
    git clone https://github.com/jamesnunn/riverscope.git
    # Change into the cloned repository
    cd riverscope
    # Create a virtual environment (note this application uses python3)
    virtualenv venv_riverscope -p python3
    # Activate the virtual environment
    source venv_riverscope/bin/activate
    # Install production dependencies
    pip install -r requirements.txt
    # Install development dependencies
    pip install -r requirements_dev.txt
    # Run tests
    pytest test
