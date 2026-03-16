

pip install numpy pandas seaborn matplotlib scikit-learn joblib jupyter nbconvert ipykernel

jupyter nbconvert --to notebook --execute adblocker_demo.ran.ipynb --output adblocker_demo.executed.ipynb --ExecutePreprocessor.timeout=1200


jupyter notebook

python -m ipykernel install --user --name email-digest --display-name "Python (email-digest)"