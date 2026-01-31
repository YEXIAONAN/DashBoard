# 小智本地TTS

## 修改模型

> [GPT-SoVITS项目的API改良与使用_gpt-sovits api-CSDN博客](https://blog.csdn.net/AAI666666/article/details/136554163)

```bash
.\runtime\python api2.py -s "SoVITS_weights/你的模型名" -g "GPT_weights/你的模型名" -dr "参考音频路径和名称" -dt "参考音频的文字内容，使用双引号括起来，确保文字内容里没有双引号" -dl zh|ja|en三者选一
```

v2版本的默认模型需要在![30e1653496513bca5dcf7cc959b91346](https://picture-01-1316374204.cos.ap-beijing.myqcloud.com/lenovo-picture/202503231624370.png)这个文件里面改





使用[小智](https://github.com/78/xiaozhi-esp32)的[开源服务器](https://github.com/xinnan-tech/xiaozhi-esp32-server), 用里面的tts接口实现, 模型使用[花儿不哭大佬](https://space.bilibili.com/5760446)的平台训练的模型(链接在最后)

> 我使用的模型和音频链接：https://pan.quark.cn/s/cbe45eb37f12

由于本人的电脑性能有限, 所以使用v1接口, 默认可以使用v2接口

## 整体流程

+ gpt方面

1. 把你的模型填入config.py文件里面
2. 如果使用v1, 把我的bat放在gpt根目录双击启动
3. 使用v2的话用vscode打开bat文件, 把里面的app.py改成app_v2.py

+ xiaozhi-server

1. 使用v2, 直接改一下v2原有的配置, 加入一个参考音频文件以及这个音频文件的实际的句子, 注意路径使用`\\`或者`/`
2. 用v1的时候, 需要把我给的那个py文件放到tts文件夹里面
3. 在server目录里面使用`python app.py`启动(安装好环境以后)

## 小智服务器

服务器的配置文件需要添加一个配置

```python
  GPT_SOVITS_V1:
    # 定义TTS API类型
    #启动tts方法：
    #python api.py
    type: gpt_sovits_v1
    url: "http://127.0.0.1:9880/"
    output_file: tmp/
    text_language: "中文"
    prompt_language: "中文"
    refer_wav_path: "E:\\alearn\\GPT-SoVITS\\纳西妲\\0.wav"
    prompt_text: "初次见面…_初次见面，我已经关注你很久了。我叫纳西妲，别看我像个孩子，我比任何一位大人都了解这个世界。所以，我可以用我的知识，换取你路上的见闻吗？"
    cut_punc: ""
    top_k: 15
    top_p: 1
    temperature: 1
    speed: 1
    inp_refs: []
```

之后把v1的文件加入tts文件夹里面

## GPT-sovits

整合包在config.py里面加入你的模型, 

![image-20250304095852653](https://picture-01-1316374204.cos.ap-beijing.myqcloud.com/picture/202503040958717.png)

之后可以使用`runtime\python.exe api.py`启动v1(或使用我的bat文件), 放在GPT-sovits的根目录里面

> 原模型链接
>
> GPT-sovits一体包链接：https://pan.baidu.com/s/1huN2HKIUctgoJdaqlemoYw?pwd=hkc0 
>
> 原神GPT-sovits模型下载链接：https://pan.baidu.com/s/1mNs9uLjHSfK7zmpIgLVe6Q?pwd=jye3 
>  其他视频资源也都发在AIGC论坛dfldata.cc，可自行拿取。欢迎交流AI图像AI语音技术（需用谷歌浏览器访问）
>
>
> 已按人物分类，.ckpt后缀模型文件放到GPT-sovits一体包的GPT_weights文件夹，.pth后缀模型文件放到SoVITS_weights文件夹
>
> 原神原始语音下载链接：https://pan.baidu.com/s/1uW_T4VcF11rwjP3NYMWgHg?pwd=d4r7 
> 用于选择不同情绪的参考音频，在合成时需要用到
>
>
> 更多使用教程和答疑，可到https://dfldata.cc/forum.php?mod=forumdisplay&fid=58 留言讨论

> **大佬的回复**
>
> GPT-SoVITS开源github发布地址（不会编程的不要下这个，下载楼下的整合包）
> https://github.com/RVC-Boss/GPT-SoVITS
> ###GPT-SoVITS解疑互助群1034332340###
> 教程文档www.yuque.com/baicaigongchang1145haoyuangong/ib3g1e
> 训练推理整合包地址：
> https://pan.baidu.com/s/1OE5qL0KreO-ASHwm6Zl9gA?pwd=mqpi（度盘超级会员才不限速下载）
> https://drive.uc.cn/s/a1fd91ae0a4f4（uc普通用户不限速）
> 云端训练地址https://www.codewithgpu.com/i/RVC-Boss/GPT-SoVITS/GPT-SoVITS-Official
>
> ###RVC变声器官 方交流讨论群1014080556，如果是RVC的用户别走错了##

## 相关教程

[AI语音生成零基础入门教学（GPT-Sovits）_哔哩哔哩_bilibili](https://www.bilibili.com/video/BV1nexGebELa/?spm_id_from=333.337.search-card.all.click)

https://www.bilibili.com/video/BV16H4y1E7YD/?spm_id_from=333.337.search-card.all.click

## 参数

使用GPT生成, 我不是很熟悉这一部分

```python
模型中的 top_k 参数主要用于控制生成内容时选择候选词的数量，特别是在自然语言处理（NLP）中的文本生成任务中。

具体来说，top_k 的作用如下：

候选词筛选：在生成每个单词时，模型会计算出所有可能的下一个单词的概率分布。top_k 参数指定只选择概率最高的 k 个单词作为候选。这可以防止生成低概率且不太合适的单词，从而提高生成文本的质量。

避免重复和无效内容：通过限制候选词的数量，top_k 使得模型更专注于选择一些更相关、更合适的单词，这样可以减少生成重复内容或无效信息的可能性。

控制生成多样性：较小的 top_k 值会使生成的内容更为集中，减少多样性；而较大的 top_k 值则允许模型从更多的候选词中选择，从而可以产生更为多样化的文本。

总之，top_k 参数是控制生成模型输出质量和多样性的重要工具。调整该参数可以帮助满足不同应用场景的需求。

top_p 参数（也称为核采样或 Nucleus Sampling）是另一种在自然语言处理模型中用于生成文本时选择候选词的方法，与 top_k 参数类似但有所不同。

top_p 参数的作用：
概率累积：top_p 通过选择概率总和达到某个阈值 p 的词汇来限制候选词的范围。具体来说，模型首先按照概率从高到低对所有候选词进行排序，然后累加概率，直到累积的概率大于或等于 p。在这个基础上，模型会从这些经过筛选的词汇中进行采样。

动态候选空间：与 top_k 不同，top_p 的候选词数量不是固定的，而是根据词汇的概率分布动态变化。例如，如果前几个高概率的单词就能达到 p，那么只会选择这几个词。如果需要更多的候选词才能达到 p，那么就会选择更多的词。

控制生成多样性与连贯性：通过调整 top_p 值，可以在生成文本的连贯性和多样性之间找到一个平衡。较低的 top_p 值可能导致生成内容更加保守和连贯，而较高的值则可能导致内容的多样性增加，文本生成变得更加随机。

总结
top_p 参数提供了一种更加灵活的方法来选择候选词，使得生成内容在一定的概率范围内保持多样性和连贯性。这对提高文本生成的质量非常有帮助，尤其是在需要创造性和多样性的应用场景中。
```

## 各种问题

+ 使用v2的时候出现404 NOT FOUND

一般是你的网址输入错了, 在最后面加一个`/tts`

+ 找不到文件

v1服务器里面报[]找不到的是正常的, 不影响, 所有的文件名使用`\\`或者`/`, 尽量不要用中文以及空格

+ CUDA错误

比较高的版本使用GPU训练, 需要使用N卡, 使用N卡还报错, 看一下驱动有没有装好

+ gpt报错400

参数没设置对, 音频的长度在3-10秒, 使用wav格式的音频, 音频文件路径记得加后缀

+ 没有声音

电脑性能不足获取使用的音频不是wav格式

[mp3转wav](https://www.freeconvert.com/zh/mp3-to-wav#:~:text=%E5%A6%82%E4%BD%95%E5%B0%86%20MP3%20%E8%BD%AC%E6%8D%A2%E4%B8%BA%20WAV%EF%BC%9F%201%20%E5%8D%95%E5%87%BB%E2%80%9C%E9%80%89%E6%8B%A9%E6%96%87%E4%BB%B6%E2%80%9D%E6%8C%89%E9%92%AE%E5%B9%B6%E9%80%89%E6%8B%A9%E6%82%A8%E7%9A%84%20MP3,%E6%96%87%E4%BB%B6%E3%80%82%202%20%E7%82%B9%E5%87%BB%E2%80%9C%E8%BD%AC%E6%8D%A2%E4%B8%BA%20WAV%E2%80%9D%E6%8C%89%E9%92%AE%E5%BC%80%E5%A7%8B%E8%BD%AC%E6%8D%A2%203%20%E5%BD%93%E7%8A%B6%E6%80%81%E5%8F%98%E4%B8%BA%E2%80%9C%E5%AE%8C%E6%88%90%E2%80%9D%E6%97%B6%EF%BC%8C%E5%8D%95%E5%87%BB%E2%80%9C%E4%B8%8B%E8%BD%BD%20WAV%E2%80%9D%E6%8C%89%E9%92%AE)
