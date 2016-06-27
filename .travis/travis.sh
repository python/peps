MASTER_REPO='python/peps'

authenticate(){
        echo "unpacking private ssh_key";
        echo $1 | base64 -d > ~/.ssh/github_deploy ;
        echo -e "Host github.com\n\tHostName github.com\n\tUser git\n\tIdentityFile ~/.ssh/github_deploy\n" >> ~/.ssh/config
        chmod 600 ~/.ssh/github_deploy
        eval `ssh-agent -s`
        ssh-add ~/.ssh/github_deploy
}

should_deploy(){
    if [[ $TRAVIS_PULL_REQUEST == false
          && $TRAVIS_REPO_SLUG == $MASTER_REPO
          && $TRAVIS_BRANCH == 'master' ]]; then
          echo 'Should deploy'
          return 0 # bash, 0 is true
    fi

    if [[ $TRAVIS_PULL_REQUEST == false
          && $TRAVIS_REPO_SLUG != $MASTER_REPO
          && $TRAVIS_BRANCH != 'master'
          && $TRAVIS_BRANCH != 'gh-pages' ]]; then
          echo 'Should deploy'
          return 0 #bash 0 is true
    fi
    return 1 # bash 1 is false
}

deploy_dir(){
    if [[ $TRAVIS_PULL_REQUEST == false
          && $TRAVIS_REPO_SLUG == $MASTER_REPO
          && $TRAVIS_BRANCH == 'master' ]] ;then
          echo "."
          return 0
    fi

    if [[ $TRAVIS_PULL_REQUEST == false
          && $TRAVIS_REPO_SLUG != $MASTER_REPO
          && $TRAVIS_BRANCH != 'master'
          && $TRAVIS_BRANCH != 'gh-pages' ]] ;then
          echo "$TRAVIS_BRANCH"
          return 0
    fi

    echo "there-is-a-bug-this-should-not-happen"
    echo "$TRAVIS_PULL_REQUEST -- $TRAVIS_REPO_SLUG!=$MASTER_REPO -- $TRAVIS_BRANCH"
}

if [ -z ${DEPLOY_KEY+x} ]; then 
    echo "DEPLOY_KEY is unset";
    echo "if you want to automatically deploy on you GH Pages"
    echo "Generate a pair of key for youfork/pep, base64 encode it"
    echo "and set is as a private ENV variable on travis named DEPLOY_KEY"
else 
    if should_deploy; 
      then
        authenticate $DEPLOY_KEY
        ORIGIN="ssh://github.com/$TRAVIS_REPO_SLUG"
        git clone $ORIGIN deploy
        echo 'cd deploy'
        cd deploy

        DEPLOY_DIR=$(deploy_dir)

        echo '=== configuring git for push ==='

        git config --global user.email "travis-ci@travis.ci"
        git config --global user.name "TravisCI BOT"
        git checkout -b gh-pages
        git config --global push.default simple
        git reset --hard origin/gh-pages
        

        mkdir -p $DEPLOY_DIR
        rm -rf $DEPLOY_DIR/*


        cp -v $HOME/build/$TRAVIS_REPO_SLUG/*.html $DEPLOY_DIR
        cp -v $HOME/build/$TRAVIS_REPO_SLUG/*.css $DEPLOY_DIR

        echo '===== git add .  ===='
        git add -A $DEPLOY_DIR
        
        echo '===== git status  ===='
        git status

        git commit -am"deploy of branch $BRANCH"
        git push origin gh-pages:gh-pages

        echo '==========================='
        echo $(echo $TRAVIS_REPO_SLUG | sed -e 's/\//.github.io\//')"/$DEPLOY_DIR/pep-0000.html"
        echo '==========================='
    else
        echo "No trying to deploy to gh-pages"
    fi 
fi
