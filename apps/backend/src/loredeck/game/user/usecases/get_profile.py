from loredeck.game.user.usecases.signup import PublicUser, to_public_user
from loredeck.shared.models import UserModel


class GetProfileUseCase:
    def execute(self, user: UserModel) -> PublicUser:
        return to_public_user(user)
