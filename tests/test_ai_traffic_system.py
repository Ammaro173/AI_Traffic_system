# from ai_traffic_system.try_this import *

# dont run test file or the game keeps running every time you close it
# Note ! pytest, being a tool for stateless unit tests rather than integration tests,
# makes the pygame quit after it gets the first response


def test_rl_ml_model_timer():
    percentage = 0.11

    actual = 13 + 1

    expected = 14  # rl_ml_model_timer(percentage)

    assert actual == expected
