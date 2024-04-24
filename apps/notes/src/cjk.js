// CJK includes the following Unicode blocks:
// \u2e80-\u2eff CJK Radicals Supplement
// \u2f00-\u2fdf Kangxi Radicals
// \u3040-\u309f Hiragana
// \u30a0-\u30ff Katakana
// \u3100-\u312f Bopomofo
// \u3200-\u32ff Enclosed CJK Letters and Months
// \u3400-\u4dbf CJK Unified Ideographs Extension A
// \u4e00-\u9fff CJK Unified Ideographs
// \uf900-\ufaff CJK Compatibility Ideographs

const CJK = '\u2e80-\u2eff\u2f00-\u2fdf\u3040-\u309f\u30a0-\u30fa\u30fc-\u30ff\u3100-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff';
const ANY_CJK = new RegExp(`[${CJK}]`);


// 不仅要识别出 cjk 和 non-cjk，cjk 内部还要细分
// 因为某些 cjk 符号和英文放在一起不应该添加空格，如全角的标点符号


// 将字符串转换为 Leaf node 列表
const textToRanges = text => {
  
  return {
    text: text,
    script:
  };
};

export default textToRanges;
