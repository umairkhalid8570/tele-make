/** @tele-module **/

export const session = tele.__session_info__ || {};
delete tele.__session_info__;
