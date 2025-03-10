"""

example path:
/mnt/glasgow/jobs/A1500_SomeProject/shots/seq220_sc01/seq220_sc01_sh180/cacheData/cfx_cloth/layerA/.versions/superman_CH0000


"""

TEST_PROJECT_PATH = "/mnt/glasgow/jobs/A1500_SomeProject"


import os


def get_cache_path(
        sequence,
        scene,
        shot,
        character,
        layer="layerA",
        namespace="CH0000",
):
    """
    get_cache_path("220", "01", "180", "superman")

    """
    project_path = os.environ["PROJECT"]

    cache_path = os.path.join(
        project_path,
        "shots",
        "seq{}_sc{}".format(sequence, scene),
        "seq{}_sc{}_sh{}".format(sequence, scene, shot),
        "cacheData",
        "cfx_cloth",
        layer,
        ".versions",
        "{}_{}".format(character, namespace)
    )

    return cache_path
