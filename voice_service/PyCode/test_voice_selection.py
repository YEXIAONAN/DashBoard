"""
测试语音选择功能
检查系统是否正确选择了对应语言的语音
"""
import pyttsx3
import sys

def test_voice_selection():
    """测试不同语言的语音选择"""
    print("=" * 60)
    print("语音选择测试")
    print("=" * 60)
    
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        print(f"\n系统可用语音数量: {len(voices)}")
        
        if len(voices) == 0:
            print("❌ 错误: 系统没有可用的语音！")
            print("请检查 Windows 语音设置")
            return False
        
        print("\n所有可用语音详情:")
        print("-" * 60)
        
        for i, voice in enumerate(voices):
            print(f"\n{i}. {voice.name}")
            print(f"   ID: {voice.id}")
            
            # 尝试获取语言信息
            try:
                if hasattr(voice, 'languages') and voice.languages:
                    print(f"   Languages: {voice.languages}")
                else:
                    print(f"   Languages: (未提供)")
            except:
                print(f"   Languages: (无法获取)")
            
            # 尝试获取其他属性
            try:
                if hasattr(voice, 'age'):
                    print(f"   Age: {voice.age}")
                if hasattr(voice, 'gender'):
                    print(f"   Gender: {voice.gender}")
            except:
                pass
        
        # 测试语言关键词匹配
        print("\n" + "=" * 60)
        print("语言匹配测试")
        print("=" * 60)
        
        language_keywords = {
            "zh": [
                'chinese', 'mandarin', 'zh-cn', 'zh_cn', 'chs', 'prc',
                'huihui', 'kangkang', 'yaoyao', 'simplified', 'china'
            ],
            "en": [
                'english', 'en-us', 'en_us', 'eng', 'usa', 'us',
                'david', 'zira', 'mark', 'united states'
            ],
            "vi": [
                'vietnamese', 'vietnam', 'vi-vn', 'vi_vn', 'vie', 'viet',
                'an', 'tiếng việt', 'tieng viet'
            ]
        }
        
        results = {}
        
        for lang, keywords in language_keywords.items():
            print(f"\n{lang.upper()} 语音:")
            print(f"关键词: {keywords}")
            
            found = False
            matched_voice = None
            
            for voice in voices:
                voice_name_lower = voice.name.lower()
                voice_id_lower = voice.id.lower()
                
                # 检查语言属性
                voice_languages = []
                if hasattr(voice, 'languages') and voice.languages:
                    voice_languages = [str(lang_attr).lower() for lang_attr in voice.languages]
                
                # 检查匹配
                name_match = any(keyword in voice_name_lower for keyword in keywords)
                id_match = any(keyword in voice_id_lower for keyword in keywords)
                lang_match = any(any(keyword in lang_attr for keyword in keywords) for lang_attr in voice_languages)
                
                if name_match or id_match or lang_match:
                    matched_voice = voice
                    print(f"✅ 找到: {voice.name}")
                    print(f"   匹配方式: 名称={name_match}, ID={id_match}, 语言属性={lang_match}")
                    found = True
                    break
            
            if not found:
                print(f"❌ 未找到 {lang} 语音")
                if lang == "vi":
                    print("\n⚠️ 越南语语音未安装！")
                    print("请按照以下步骤安装:")
                    print("1. 打开 Windows 设置 (Win + I)")
                    print("2. 进入 时间和语言 → 语音")
                    print("3. 点击 添加语音")
                    print("4. 搜索并安装 'Microsoft An - Vietnamese (Vietnam)'")
                    print("5. 重启电脑")
                    print("\n详细说明请查看: install_vietnamese_voice.md")
            
            results[lang] = found
        
        # 测试语音合成
        print("\n" + "=" * 60)
        print("语音合成测试")
        print("=" * 60)
        
        test_texts = {
            "zh": "你好，这是中文语音测试",
            "en": "Hello, this is an English voice test",
            "vi": "Xin chào, đây là bài kiểm tra giọng nói tiếng Việt"
        }
        
        for lang, text in test_texts.items():
            if not results.get(lang):
                print(f"\n跳过 {lang.upper()} (语音未找到)")
                continue
            
            print(f"\n测试 {lang.upper()} 语音:")
            print(f"文本: {text}")
            
            # 查找语音
            keywords = language_keywords.get(lang, [])
            selected_voice = None
            
            for voice in voices:
                voice_name_lower = voice.name.lower()
                voice_id_lower = voice.id.lower()
                
                if any(keyword in voice_name_lower or keyword in voice_id_lower for keyword in keywords):
                    selected_voice = voice
                    break
            
            if selected_voice:
                print(f"使用语音: {selected_voice.name}")
                try:
                    engine.setProperty('voice', selected_voice.id)
                    
                    # 生成语音文件
                    output_file = f"test_{lang}.wav"
                    engine.save_to_file(text, output_file)
                    engine.runAndWait()
                    print(f"✅ 已生成: {output_file}")
                except Exception as e:
                    print(f"❌ 生成失败: {e}")
            else:
                print(f"❌ 未找到 {lang} 语音，跳过")
        
        # 总结
        print("\n" + "=" * 60)
        print("测试总结")
        print("=" * 60)
        
        total = len(results)
        passed = sum(1 for found in results.values() if found)
        
        print(f"\n语音可用性: {passed}/{total}")
        for lang, found in results.items():
            status = "✅ 可用" if found else "❌ 不可用"
            print(f"  {lang.upper()}: {status}")
        
        if not results.get("vi"):
            print("\n⚠️ 重要提示:")
            print("越南语语音未安装，请查看 install_vietnamese_voice.md 获取安装指南")
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
        
        if passed < total:
            print("\n请播放生成的 .wav 文件检查语音是否正确")
            print("如果越南语不可用，请按照 install_vietnamese_voice.md 安装")
        else:
            print("\n✅ 所有语音都可用！")
            print("请播放生成的 .wav 文件检查语音质量")
        
        return passed == total
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_voice_selection()
    sys.exit(0 if success else 1)
