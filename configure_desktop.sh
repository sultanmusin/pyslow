SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PATH_TO_DESKTOP_FILE="$SCRIPT_DIR/slow_control.desktop"

APP_DIR_SUBSTITUTE='{APP_DIR}'

cp $PATH_TO_DESKTOP_FILE.skel $PATH_TO_DESKTOP_FILE
sed -i -e "s#${APP_DIR_SUBSTITUTE}#${SCRIPT_DIR}#g" $PATH_TO_DESKTOP_FILE

sudo desktop-file-install $PATH_TO_DESKTOP_FILE