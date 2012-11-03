Bluebell
========

Django client for API demonstration

# checkout application from git
git clone https://github.com/pbs/bluebell.git

#create virtual environment
cd bluebell
virtualenv ve

#activate virtual environment
source ve/bin/activate

# install requirements
pip install -r requirements.txt

# install elastic beanstalk CLI
cd <some directory outside of this django application>
wget https://s3.amazonaws.com/elasticbeanstalk/cli/AWS-ElasticBeanstalk-CLI-2.1.zip
unzip AWS-ElasticBeanstalk-CLI-2.1.zip
alias eb="python2.7 /path/to/elastic/beanstalk/directory/eb/macosx/python2.7/eb"
`
# configure
cd <django application directory>
eb init

# the elastic beanstalk command line utility will then ask a bunch of questions
# to configure the new environment

# start application
eb start

# to deploy new code / environment:
git aws.push
