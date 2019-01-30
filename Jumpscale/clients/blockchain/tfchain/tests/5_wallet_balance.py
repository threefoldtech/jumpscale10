from Jumpscale import j

from Jumpscale.clients.blockchain.tfchain.stub.ExplorerClientStub import TFChainExplorerGetClientStub

def main(self):
    """
    to run:

    js_shell 'j.clients.tfchain.test(name="wallet_balance")'
    """

    # create a tfchain client for devnet
    c = j.clients.tfchain.new("mydevclient", network_type="DEV")
    # or simply `c = j.tfchain.clients.mydevclient`, should the client already exist

    # (we replace internal client logic with custom logic as to ensure we can test without requiring an active network)
    explorer_client = TFChainExplorerGetClientStub()
    explorer_client.hash_add('014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a', '{"hashtype":"unlockhash","block":{"minerpayoutids":null,"transactions":null,"rawblock":{"parentid":"0000000000000000000000000000000000000000000000000000000000000000","timestamp":0,"pobsindexes":{"BlockHeight":0,"TransactionIndex":0,"OutputIndex":0},"minerpayouts":null,"transactions":null},"blockid":"0000000000000000000000000000000000000000000000000000000000000000","difficulty":"0","estimatedactivebs":"0","height":0,"maturitytimestamp":0,"target":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"totalcoins":"0","arbitrarydatatotalsize":0,"minerpayoutcount":0,"transactioncount":0,"coininputcount":0,"coinoutputcount":0,"blockstakeinputcount":0,"blockstakeoutputcount":0,"minerfeecount":0,"arbitrarydatacount":0},"blocks":null,"transaction":{"id":"0000000000000000000000000000000000000000000000000000000000000000","height":0,"parent":"0000000000000000000000000000000000000000000000000000000000000000","rawtransaction":{"version":0,"data":{"coininputs":[],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},"transactions":[{"id":"0b5d7509e467b943af12db2d73ddb78a5ec8cfdf64c3c6ecacb2de4af68bdc4d","height":33,"parent":"40e281daee6f113b788d64b8247381c36fe4885233a7475c9be2cce852e1696e","rawtransaction":{"version":1,"data":{"coininputs":[{"parentid":"a3c8f44d64c0636018a929d2caeec09fb9698bfdcbfa3a8225585a51e09ee563","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"e5b69be3b385f0a33f7978e0d6af30cf37c975bbb99d0f3d06f199cd579d3e6854f6cb398c88082e438c89d11d04de0e7d3b2876e250d4ba8ae457f88547f605"}}}],"coinoutputs":[{"value":"1000000000000","condition":{"type":1,"data":{"unlockhash":"014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a"}}},{"value":"99998999000000000","condition":{"type":1,"data":{"unlockhash":"01f68299b26a89efdb4351a61c3a062321d23edbc1399c8499947c1313375609adbbcd3977363c"}}}],"minerfees":["1000000000"]}},"coininputoutputs":[{"value":"100000000000000000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}},"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}],"coinoutputids":["75f297550acfa48490c21490f82c3c308326c16f950e17ef3a286486065a51b8","6d157a1eb23cadde122192869bc51e2a0fe44a2d8aba898cbdda8b7218a0f8cb"],"coinoutputunlockhashes":["014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a","01f68299b26a89efdb4351a61c3a062321d23edbc1399c8499947c1313375609adbbcd3977363c"],"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},{"id":"1b144b89c4b65cc67416e27286e802c50f78bc7326b4b0e5f6f967f99cc39419","height":200,"parent":"68e3886c9a4c59dea8c7a0eb138ede0e83716b995fd8ebfa5dfc766bfb349565","rawtransaction":{"version":1,"data":{"coininputs":[{"parentid":"6d157a1eb23cadde122192869bc51e2a0fe44a2d8aba898cbdda8b7218a0f8cb","fulfillment":{"type":1,"data":{"publickey":"ed25519:00bde9571b30e1742c41fcca8c730183402d967df5b17b5f4ced22c677806614","signature":"05c72055d4cca6d8620fd7453c89ac8deaf92c38e366604dc6405cb097321b74e2e5f7ece15b440f4af5721b8aa6ea1f57f4fce44d2a2c6c0fb7a1e068a0480d"}}}],"coinoutputs":[{"value":"500000000000","condition":{"type":1,"data":{"unlockhash":"014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a"}}},{"value":"99998498000000000","condition":{"type":1,"data":{"unlockhash":"0161fbcf58efaeba8813150e88fc33405b3a77d51277a2cdf3f4d2ab770de287c7af9d456c4e68"}}}],"minerfees":["1000000000"]}},"coininputoutputs":[{"value":"99998999000000000","condition":{"type":1,"data":{"unlockhash":"01f68299b26a89efdb4351a61c3a062321d23edbc1399c8499947c1313375609adbbcd3977363c"}},"unlockhash":"01f68299b26a89efdb4351a61c3a062321d23edbc1399c8499947c1313375609adbbcd3977363c"}],"coinoutputids":["1d686b8dfe44dfbfea55f327a52d9701a52938cb2c829f709dfb8059bc0e5f87","e27ed8bbe45177fafdfd7d21394ff483b8bde24f551dd927a046a0b7c37ec228"],"coinoutputunlockhashes":["014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a","0161fbcf58efaeba8813150e88fc33405b3a77d51277a2cdf3f4d2ab770de287c7af9d456c4e68"],"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},{"id":"5ab2604c7d54dd9ea39d829724e46deb8bbf2889d8627a3bb3b57907c6f4dff4","height":1433,"parent":"6b9fdad35096c5a84dcdb6e3e9ec2a8c7562f567e05b1207a7f9330ed51582bb","rawtransaction":{"version":1,"data":{"coininputs":[{"parentid":"e27ed8bbe45177fafdfd7d21394ff483b8bde24f551dd927a046a0b7c37ec228","fulfillment":{"type":1,"data":{"publickey":"ed25519:41e84f3b0f6a06dd7e45ded4d0e227869725355b73906b82d9e3ffc0b6b01416","signature":"47a4d1a6aeb7403ea5c2cbcc26f84bb1964aadcb8765696db4a623694991f794663b860898db53401dd4324477c43f9fff177b74909201a03e131c2cd885cc0d"}}}],"coinoutputs":[{"value":"500000000000","condition":{"type":1,"data":{"unlockhash":"014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a"}}},{"value":"99997997000000000","condition":{"type":1,"data":{"unlockhash":"0137f6f647a3c8019f6ae215ed09902c308efbf555b3520d2112d2b18cb577e40804d6fc5fafd2"}}}],"minerfees":["1000000000"]}},"coininputoutputs":[{"value":"99998498000000000","condition":{"type":1,"data":{"unlockhash":"0161fbcf58efaeba8813150e88fc33405b3a77d51277a2cdf3f4d2ab770de287c7af9d456c4e68"}},"unlockhash":"0161fbcf58efaeba8813150e88fc33405b3a77d51277a2cdf3f4d2ab770de287c7af9d456c4e68"}],"coinoutputids":["b90422bad2dffde79f0a46bd0a41055cf7974b080e115d76f69891ca31d31f11","f386312779f382f16fa836038b3d25536b928ba88ae1afa1f8c0e8dc25c0ba16"],"coinoutputunlockhashes":["014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a","0137f6f647a3c8019f6ae215ed09902c308efbf555b3520d2112d2b18cb577e40804d6fc5fafd2"],"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},{"id":"81d81b413fc8af3e528478e639d5a6e999e5e96611593cd2458b4d2d7abc3880","height":1433,"parent":"6b9fdad35096c5a84dcdb6e3e9ec2a8c7562f567e05b1207a7f9330ed51582bb","rawtransaction":{"version":1,"data":{"coininputs":[{"parentid":"f386312779f382f16fa836038b3d25536b928ba88ae1afa1f8c0e8dc25c0ba16","fulfillment":{"type":1,"data":{"publickey":"ed25519:4e42a2fcfc0963d6fa7bb718fd088d9b6544331e8562d2743e730cdfbedeb55a","signature":"4abae694cf6a6408eca6f034ea2ec6930b9a73303c3e70d3444cf36a9966b0c4cc1b65168c23640affb5bdeae539ea583d42da52c58d21f59b71c288b3faef0e"}}}],"coinoutputs":[{"value":"2000000000000","condition":{"type":1,"data":{"unlockhash":"014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a"}}},{"value":"99995996000000000","condition":{"type":1,"data":{"unlockhash":"0173f82c3ee74286c33fee8d883a7e9e759c6230b9e4e956ef233d7202bde69da45054270eef99"}}}],"minerfees":["1000000000"],"arbitrarydata":"Zm9vYmFy"}},"coininputoutputs":[{"value":"99997997000000000","condition":{"type":1,"data":{"unlockhash":"0137f6f647a3c8019f6ae215ed09902c308efbf555b3520d2112d2b18cb577e40804d6fc5fafd2"}},"unlockhash":"0137f6f647a3c8019f6ae215ed09902c308efbf555b3520d2112d2b18cb577e40804d6fc5fafd2"}],"coinoutputids":["d1f74e90eba8095e78f08a6284c7b76d4cda86b06ac742062d6e0e02dc4607eb","1edccdb04100ffd05d97431b6798533fa57dc7ed1ea58c75f0f445fb64442d6e"],"coinoutputunlockhashes":["014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a","0173f82c3ee74286c33fee8d883a7e9e759c6230b9e4e956ef233d7202bde69da45054270eef99"],"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false}],"multisigaddresses":["039e16ed27b2dfa3a5bbb1fa2b5f240ba7ff694b34a52bfc5bed6d4c3b14b763c011d7503ccb3a"],"unconfirmed":false}')
    explorer_client.chain_info = '{"blockid":"dabfeb1c9535e22dd562f728e852f2e714f7e330c850066e7f7cb3c1b4b1d2ec","difficulty":"22957","estimatedactivebs":"2265","height":1799,"maturitytimestamp":1548856333,"target":[0,2,218,204,69,189,159,63,170,208,45,36,127,38,76,44,75,135,241,125,104,230,68,108,12,26,177,178,210,10,223,51],"totalcoins":"0","arbitrarydatatotalsize":6,"minerpayoutcount":1803,"transactioncount":1805,"coininputcount":9,"coinoutputcount":11,"blockstakeinputcount":1799,"blockstakeoutputcount":1800,"minerfeecount":5,"arbitrarydatacount":1}'
    explorer_client.hash_add('dabfeb1c9535e22dd562f728e852f2e714f7e330c850066e7f7cb3c1b4b1d2ec', '{"hashtype":"blockid","block":{"minerpayoutids":["ad16dd3a70cca599ebf5093353ff1f2be20203575b67ab9f6dfe643d8b475c4a"],"transactions":[{"id":"bb10422e7932bdbcf7ce8fc069f8760053805f03b85c14a48e0581429236ad91","height":1799,"parent":"dabfeb1c9535e22dd562f728e852f2e714f7e330c850066e7f7cb3c1b4b1d2ec","rawtransaction":{"version":1,"data":{"coininputs":null,"blockstakeinputs":[{"parentid":"3ab4391af3267fe3f5a7cc1ce89692dee45d455cfd592ea1c1394d8b7c63c9a6","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"2c6233104c405eecb42e10267a0bb92f0133f643d2e59453c44a6f66175cbc4f0e27ad5e824e1ee4bfb7747b4664312369ed4ba97e1e1d6e57e0a24e901ac40d"}}}],"blockstakeoutputs":[{"value":"3000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}}}],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":[{"value":"3000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}},"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}],"blockstakeoutputids":["ccca3417261a33a6ce0a5bbbb4d96679ceb0c5a72e710449b5a30b3598113ffa"],"blockstakeunlockhashes":["015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"],"unconfirmed":false}],"rawblock":{"parentid":"72d9531016b2ebf4428f2ebc5b2299c2b2af7e84ac245b8f4eb9d2acff214fcb","timestamp":1548856456,"pobsindexes":{"BlockHeight":1798,"TransactionIndex":0,"OutputIndex":0},"minerpayouts":[{"value":"10000000000","unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}],"transactions":[{"version":1,"data":{"coininputs":null,"blockstakeinputs":[{"parentid":"3ab4391af3267fe3f5a7cc1ce89692dee45d455cfd592ea1c1394d8b7c63c9a6","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"2c6233104c405eecb42e10267a0bb92f0133f643d2e59453c44a6f66175cbc4f0e27ad5e824e1ee4bfb7747b4664312369ed4ba97e1e1d6e57e0a24e901ac40d"}}}],"blockstakeoutputs":[{"value":"3000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}}}],"minerfees":null}}]},"blockid":"dabfeb1c9535e22dd562f728e852f2e714f7e330c850066e7f7cb3c1b4b1d2ec","difficulty":"22957","estimatedactivebs":"2265","height":1799,"maturitytimestamp":1548856333,"target":[0,2,218,204,69,189,159,63,170,208,45,36,127,38,76,44,75,135,241,125,104,230,68,108,12,26,177,178,210,10,223,51],"totalcoins":"0","arbitrarydatatotalsize":6,"minerpayoutcount":1803,"transactioncount":1805,"coininputcount":9,"coinoutputcount":11,"blockstakeinputcount":1799,"blockstakeoutputcount":1800,"minerfeecount":5,"arbitrarydatacount":1},"blocks":null,"transaction":{"id":"0000000000000000000000000000000000000000000000000000000000000000","height":0,"parent":"0000000000000000000000000000000000000000000000000000000000000000","rawtransaction":{"version":0,"data":{"coininputs":[],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},"transactions":null,"multisigaddresses":null,"unconfirmed":false}')
    explorer_client.hash_add('039e16ed27b2dfa3a5bbb1fa2b5f240ba7ff694b34a52bfc5bed6d4c3b14b763c011d7503ccb3a', '{"hashtype":"unlockhash","block":{"minerpayoutids":null,"transactions":null,"rawblock":{"parentid":"0000000000000000000000000000000000000000000000000000000000000000","timestamp":0,"pobsindexes":{"BlockHeight":0,"TransactionIndex":0,"OutputIndex":0},"minerpayouts":null,"transactions":null},"blockid":"0000000000000000000000000000000000000000000000000000000000000000","difficulty":"0","estimatedactivebs":"0","height":0,"maturitytimestamp":0,"target":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"totalcoins":"0","arbitrarydatatotalsize":0,"minerpayoutcount":0,"transactioncount":0,"coininputcount":0,"coinoutputcount":0,"blockstakeinputcount":0,"blockstakeoutputcount":0,"minerfeecount":0,"arbitrarydatacount":0},"blocks":null,"transaction":{"id":"0000000000000000000000000000000000000000000000000000000000000000","height":0,"parent":"0000000000000000000000000000000000000000000000000000000000000000","rawtransaction":{"version":0,"data":{"coininputs":[],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},"transactions":[{"id":"4c70a0406f36cf354edf87642df3f34568fd0a89c052a81d11cc6e4f8fbf685e","height":45,"parent":"f7b78b17d581ff9e58ffbcce1701d4dcadb0781590ca68e839def0dc98b0360a","rawtransaction":{"version":1,"data":{"coininputs":[{"parentid":"7d4a100fc3bc08b2bdd1284c17260dd2bd6b55fd6c1429dbbd683bf362d92b50","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"c34b8ca1ab08930bc68d61026af504d62d8a8bbda9b79ae01a387560fba22d39b12021e16566732b742ea686f997b3c19c807523797cdc0d74a4d25123691004"}}},{"parentid":"83503f9cea00d562e0460eace93159a4c4dd00df4703c96947e81885b46da04c","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"f6eea681a259baf14433ac55b4293b22ca2056810ee8fed2129039224d14558f54ca58c6d96e9885cb20ecdf7e64ba81d1a83c6e9a42bf9464287fa6359d360c"}}},{"parentid":"578aa43de72b42b4f4547c5ddc7f61736b1cac206e1789bc89fcd9333cf3d1f3","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"a0521d14dfe4a0c9b8b57ed361d738b48b6a8346097246effe0b4ee67b6fecbc3a90e4671ddc0b164f6c2839df249bb5998f10216a4a674ba8d24b8ad6bdf808"}}},{"parentid":"5a1454762e6895431e1b9e4e435e4d0ad60a3881843ac46b88e220771055ca87","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"900e7868780e67bcb68af3ec6976e84289850d0db59210d4689b1c0e2deb3164b9e93eb9ee5a38850f2319463b0845163e1eee443d7b645c59485c2aa0837707"}}},{"parentid":"c04ebebe17a1759457eecaf4d5d33f5ddbe8d154b0be1606f05bc8fd02ab9cd4","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"e992b1cd3347b5362e820166d5929de7c682130c7143fc4c9ff3156f5d44110753687697a0154a2043290b3f022e2537f3e3a6807caf9150f8c255d74e386d0a"}}}],"coinoutputs":[{"value":"42000000000","condition":{"type":4,"data":{"unlockhashes":["01ffd7c884aa869056bfb832d957bb71a0005fee13c19046cebec84b3a5047ee8829eab070374b","014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a"],"minimumsignaturecount":1}}},{"value":"7000000000","condition":{"type":1,"data":{"unlockhash":"01972837ee396f22f96846a0c700f9cf7c8fa83ab4110da91a1c7d02f94f28ff03e45f1470df82"}}}],"minerfees":["1000000000"]}},"coininputoutputs":[{"value":"10000000000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}},"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"},{"value":"10000000000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}},"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"},{"value":"10000000000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}},"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"},{"value":"10000000000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}},"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"},{"value":"10000000000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}},"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}],"coinoutputids":["29152fe03a2c8782fcbd670579686088c52be83fa3870f5f0788073d97fb5fb2","0fc9b16bb180cd8f8a7144d65e6c8fca66994a4ccaee42e324289d4039ab2841"],"coinoutputunlockhashes":["039e16ed27b2dfa3a5bbb1fa2b5f240ba7ff694b34a52bfc5bed6d4c3b14b763c011d7503ccb3a","01972837ee396f22f96846a0c700f9cf7c8fa83ab4110da91a1c7d02f94f28ff03e45f1470df82"],"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false}],"multisigaddresses":null,"unconfirmed":false}')
    c._explorer_get = explorer_client.explorer_get

    # the devnet genesis seed is the seed of the wallet,
    # which receives all block stakes and coins in the genesis block of the tfchain devnet
    DEVNET_GENESIS_SEED="image orchard airport business cost work mountain obscure flee alpha alert salmon damage engage trumpet route marble subway immune short tide young cycle attract"

    # create a new devnet wallet
    w = c.wallets.new("mywallet", seed=DEVNET_GENESIS_SEED)
    # we create a new wallet using an existing seed,
    # such that our seed is used and not a new randomly generated seed

    # a tfchain (JS) wallet uses the underlying tfchain client for all its
    # interaction with the tfchain network
    assert w.network_type == "DEV"

    # getting the balance of a wallet is as easy as getting the 'balance' property
    balance = w.balance

    # the available and locked tokens can be easily checked
    assert str(balance.available) == '4000000000000'
    assert str(balance.locked) == '0'

    # MultiSig wallets can be easily checked as well
    assert str(balance.wallets['039e16ed27b2dfa3a5bbb1fa2b5f240ba7ff694b34a52bfc5bed6d4c3b14b763c011d7503ccb3a'].available) == '42000000000'
    assert str(balance.wallets['039e16ed27b2dfa3a5bbb1fa2b5f240ba7ff694b34a52bfc5bed6d4c3b14b763c011d7503ccb3a'].locked) == '0'
    # MultiSig wallets balance reports also contain the owners and signatures required
    msbalance = balance.wallets['039e16ed27b2dfa3a5bbb1fa2b5f240ba7ff694b34a52bfc5bed6d4c3b14b763c011d7503ccb3a']
    assert len(msbalance.owners) == 2
    assert '01ffd7c884aa869056bfb832d957bb71a0005fee13c19046cebec84b3a5047ee8829eab070374b' in msbalance.owners
    assert '014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a' in msbalance.owners
    assert msbalance.signature_count == 1

    # a balance can be used for funding amounts
    # (NOTE that is it up to you to ensure that your balance object is used only until it becomes out of date)
    outputs, remainder = balance.fund(500)
    assert str(remainder) == '499999999500'
    assert str(sum([co.value for co in outputs])) == '500000000000'
