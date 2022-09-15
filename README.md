# Alleviating the cold-start playlist continuation in music recommendation using latent semantic indexing

The cold-start problem is a grand challenge in music recommender systems aiming to provide users with a better and continuous music listening experience. 
When a new user creates a playlist, the recommender system remains in a cold-startstate until enough information is collected to identify the user’s musical taste. 
In such cases, playlist metadata, such as title or description, have been successfully employed to create intent recommendation models. 
In this paper, we propose a multistage retrieval system utilizing user-generated titles to alleviate the cold-start problem in automatic playlist continuation.
Initially, playlists are clustered to form a music documents collection. 
Then, the system applies latent semantic indexing to the collection to discover hidden patterns between tracks and playlist titles. 
For similarity calculation, singular value decomposition is performed on a track-cluster matrix. 
When the system is given a new playlist as a cold-start instance, it first retrieves neighboring clusters and then produces a ranked list of recommendations by weighting candidate tracks in these clusters. 
We scrutinize the performance of the proposed system on a large, real-world music playlists dataset supplied by the Spotify platform. 
Our empirical results show that the proposed system outperforms the state-of-the-art approaches and improves recommendation accuracy significantly in three primary evaluation metrics.

### Citation
If you build upon the proposed idea or use the source code, please cite the following paper:

Yürekli, A., Kaleli, C. & Bilge, A. Alleviating the cold-start playlist continuation in music recommendation using latent semantic indexing. 
Int J Multimed Info Retr 10, 185–198 (2021). https://doi.org/10.1007/s13735-021-00214-5
