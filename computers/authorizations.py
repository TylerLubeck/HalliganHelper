from tastypie.exceptions import Unauthorized
from tastypie.authorization import Authorization


class AuthorizationMethods(object):
    def _superuser_or_group(self, object_list, bundle):
        user = bundle.request.user
        if not user.is_superuser or not user.is_active:
            raise Unauthorized("You are not authorized!")

    def _authenticated_active_user(self, object_list, bundle):
        user = bundle.request.user
        if not user.is_authenticated() or not user.is_active:
            raise Unauthorized("You are not authorized!")


class AdminWriteAuthorization(Authorization, AuthorizationMethods):
    def read_list(self, object_list, bundle):
        self._authenticated_active_user(object_list, bundle)
        return object_list

    def read_detail(self, object_list, bundle):
        self._authenticated_active_user(object_list, bundle)
        return True

    def create_list(self, object_list, bundle):
        self._superuser_or_group(object_list, bundle)
        return object_list

    def create_detail(self, object_list, bundle):
        self._authenticated_active_user()
        return True

    def update_list(self, object_list, bundle):
        self._superuser_or_group(object_list, bundle)
        return object_list

    def update_detail(self, object_list, bundle):
        self._superuser_or_group(object_list, bundle)
        return True

    def delete_list(self, object_list, bundle):
        self._superuser_or_group(object_list, bundle)
        return object_list

    def delete_detail(self, object_list, bundle):
        self._superuser_or_group(object_list, bundle)
        return True


class UserUpdateableAuthorization(Authorization, AuthorizationMethods):
    def read_list(self, object_list, bundle):
        self._authenticated_active_user(object_list, bundle)
        return object_list

    def read_detail(self, object_list, bundle):
        self._authenticated_active_user(object_list, bundle)
        return True

    def create_list(self, object_list, bundle):
        self._superuser_or_group(object_list, bundle)
        return object_list

    def create_detail(self, object_list, bundle):
        self._authenticated_active_user()
        return True

    def update_list(self, object_list, bundle):
        self._superuser_or_group()
        return object_list

    def update_detail(self, object_list, bundle):
        """Check that the user is authenticated and active, then
        return False.

        This needs to be implemented in a subclass to actually check
        ownership of various objects
        """
        self._authenticated_active_user()
        return False

    def delete_list(self, object_list, bundle):
        self._superuser_or_group(object_list, bundle)
        return object_list

    def delete_detail(self, object_list, bundle):
        self._superuser_or_group(object_list, bundle)
        return True
