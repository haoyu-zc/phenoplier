import numpy as np
import pandas as pd
from tqdm import tqdm


def reset_estimator(estimator_obj):
    for attr in dir(estimator_obj):
        if attr.startswith('_') or not attr.endswith('_'):
            continue

        delattr(estimator_obj, attr)


def generate_ensemble(data, clusterers: dict, attributes: list):
    """

    Args:
        clusterers: a dictionary with clusterers, like:
        {
            'k-means #1': KMeans(n_clusters=2),
            ...
        }
        attributes: list of attributes to save in the final dataframe

    Returns:

    """
    ensemble = []

    for clus_name, clus_obj in tqdm(clusterers.items(), total=len(clusterers)):
        # get partition and remove noisy points
        partition = clus_obj.fit_predict(data).astype(float)
        partition[partition < 0] = np.nan

        # get number of clusters
        partition_no_nan = partition[~np.isnan(partition)]
        n_clusters = np.unique(partition_no_nan).shape[0]

        # stop if n_clusters <= 1
        if n_clusters <= 1:
            reset_estimator(clus_obj)
            continue

        res = pd.Series({
            'clusterer_id': clus_name,
            'clusterer_params': str(clus_obj.get_params()),
            'partition': partition,
        })

        for attr in attributes:
            if attr == 'n_clusters' and not hasattr(clus_obj, attr):
                res[attr] = n_clusters
            else:
                res[attr] = getattr(clus_obj, attr)

        ensemble.append(res)

        reset_estimator(clus_obj)

    return pd.DataFrame(ensemble).set_index('clusterer_id')
