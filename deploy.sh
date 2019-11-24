#!/bin/bash
echo "Removing existing files..."
rm -rf /var/staging/Rhythm
cd /var/staging
echo "Creating Rhythm folder..."
mkdir Rhythm
# Clone Rhythm, the Django project
git clone --depth 1 https://github.com/qiuosier/Rhythm.git
cd Rhythm
# Clone Virgo as Django app
git clone --depth 1 https://github.com/qiuosier/Virgo.git
# Update submodules, this will clone Aries
git submodule update --init --recursive
# Copy credentials
gsutil cp gs://qqin.page/Rhythm/private.py /var/staging/Rhythm/rhythm/private.py
# Activate virtual environment
source /var/envs/Rhythm/bin/activate
# Install dependencies
pip install --no-cache-dir -r /var/Rhythm/requirements.txt
pip install --no-cache-dir -r /var/Rhythm/Virgo/requirements.txt
# Collect statics
python manage.py collectstatic
# Deply the code
echo "Copying source code..."
rsync -r -d --info=progress2 /var/staging/Rhythm /var/
# END
