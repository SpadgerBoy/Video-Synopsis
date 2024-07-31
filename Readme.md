**Optimization of Federated Learning Based on Reinforcement Learning**



The FLPPO model adopts the proximal policy optimization (PPO) algorithm. In the experiment, the action space of the model is greatly compressed through the grouping strategy, so that the agent can traverse in a short time. During the training, let the agent help select the equipment participating in the training in each round, and encourage it to improve the accuracy of the global model selection, so as to accelerate the convergence of the global model and reduce the number of communication rounds. At the same time, a dynamic probability node selection strategy is introduced into the FLPPO model to reduce the long-tail waiting effect caused by network delay and shorten the training time.



The required dependencies are in the requirements. txt file

Run code：

```
python run.py --config=configs/config.json 
```





FedAvg and Cluster control groups were set up for FLPPO in the experiment.



Label "IID": The IID distribution of each client data serves as the "upper limit" for experimental performance comparison.
Label "FedAvg": Non IID distribution of data for each client, using FedAvg algorithm to randomly select clients for aggregation and updating, generally used as the "lower limit" for experimental performance comparison.
Tag "Cluster": The data distribution is the same as in FedAvg, and clustering is performed based on the characteristics of the client model. Each round, a cluster of clients is selected for aggregation and updating.
Label "FLPPO": The data distribution is the same as in FedAvg, the experimental algorithm in this article. Using the intelligent agent in PPO algorithm to assist in selecting the client for each round.

![image-20240731141855297](assets/image-20240731141855297.png)



![image-20240731142020488](assets/image-20240731142020488.png)

![image-20240731142032378](assets/image-20240731142032378.png)



![image-20240731142045730](assets/image-20240731142045730.png)