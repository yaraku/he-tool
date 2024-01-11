/*
 * Copyright (C) 2023 Yaraku, Inc.
 *
 * This file is part of Human Evaluation Tool.
 *
 * Human Evaluation Tool is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by the
 * Free Software Foundation, either version 3 of the License,
 * or (at your option) any later version.
 *
 * Human Evaluation Tool is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 * or FITNESS FOR A PARTICULAR PURPOSE.
 * See the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along with
 * Human Evaluation Tool. If not, see <https://www.gnu.org/licenses/>.
 *
 * Written by Giovanni G. De Giacomo <giovanni@yaraku.com>, August 2023
 */

export default function LanguageSelector(props) {
  return (
    <select
      className={props.className}
      id={props.id}
      name={props.name}
      onChange={props.onChange}
      required={props.required}
      value={props.value}
    >
      <option value="ab">Abkhazian</option>
      <option value="aa">Afar</option>
      <option value="af">Afrikaans</option>
      <option value="ak">Akan</option>
      <option value="sq">Albanian</option>
      <option value="am">Amharic</option>
      <option value="ar">Arabic</option>
      <option value="an">Aragonese</option>
      <option value="hy">Armenian</option>
      <option value="as">Assamese</option>
      <option value="av">Avaric</option>
      <option value="ae">Avestan</option>
      <option value="ay">Aymara</option>
      <option value="az">Azerbaijani</option>
      <option value="bm">Bambara</option>
      <option value="ba">Bashkir</option>
      <option value="eu">Basque</option>
      <option value="be">Belarusian</option>
      <option value="bn">Bengali</option>
      <option value="bh">Bihari languages</option>
      <option value="bi">Bislama</option>
      <option value="nb">Bokmål Norwegian; Norwegian Bokmål</option>
      <option value="bs">Bosnian</option>
      <option value="br">Breton</option>
      <option value="bg">Bulgarian</option>
      <option value="my">Burmese</option>
      <option value="ca">Catalan; Valencian</option>
      <option value="km">Central Khmer</option>
      <option value="ch">Chamorro</option>
      <option value="ce">Chechen</option>
      <option value="ny">Chichewa; Chewa; Nyanja</option>
      <option value="zh">Chinese</option>
      <option value="cu">
        Church Slavic; Old Slavonic; Church Slavonic; Old Bulgarian; Old Church
        Slavonic
      </option>
      <option value="cv">Chuvash</option>
      <option value="kw">Cornish</option>
      <option value="co">Corsican</option>
      <option value="cr">Cree</option>
      <option value="hr">Croatian</option>
      <option value="cs">Czech</option>
      <option value="da">Danish</option>
      <option value="dv">Divehi; Dhivehi; Maldivian</option>
      <option value="nl">Dutch; Flemish</option>
      <option value="dz">Dzongkha</option>
      <option value="en">English</option>
      <option value="eo">Esperanto</option>
      <option value="et">Estonian</option>
      <option value="ee">Ewe</option>
      <option value="fo">Faroese</option>
      <option value="fj">Fijian</option>
      <option value="fi">Finnish</option>
      <option value="fr">French</option>
      <option value="ff">Fulah</option>
      <option value="gd">Gaelic; Scottish Gaelic</option>
      <option value="gl">Galician</option>
      <option value="lg">Ganda</option>
      <option value="ka">Georgian</option>
      <option value="de">German</option>
      <option value="el">Greek, Modern</option>
      <option value="gn">Guarani</option>
      <option value="gu">Gujarati</option>
      <option value="ht">Haitian; Haitian Creole</option>
      <option value="ha">Hausa</option>
      <option value="he">Hebrew</option>
      <option value="hz">Herero</option>
      <option value="hi">Hindi</option>
      <option value="ho">Hiri Motu</option>
      <option value="hu">Hungarian</option>
      <option value="is">Icelandic</option>
      <option value="io">Ido</option>
      <option value="ig">Igbo</option>
      <option value="id">Indonesian</option>
      <option value="ia">
        Interlingua (International Auxiliary Language Association)
      </option>
      <option value="ie">Interlingue; Occidental</option>
      <option value="iu">Inuktitut</option>
      <option value="ik">Inupiaq</option>
      <option value="ga">Irish</option>
      <option value="it">Italian</option>
      <option value="ja">Japanese</option>
      <option value="jv">Javanese</option>
      <option value="kl">Kalaallisut; Greenlandic</option>
      <option value="kn">Kannada</option>
      <option value="kr">Kanuri</option>
      <option value="ks">Kashmiri</option>
      <option value="kk">Kazakh</option>
      <option value="ki">Kikuyu; Gikuyu</option>
      <option value="rw">Kinyarwanda</option>
      <option value="ky">Kirghiz; Kyrgyz</option>
      <option value="kv">Komi</option>
      <option value="kg">Kongo</option>
      <option value="ko">Korean</option>
      <option value="kj">Kuanyama; Kwanyama</option>
      <option value="ku">Kurdish</option>
      <option value="lo">Lao</option>
      <option value="la">Latin</option>
      <option value="lv">Latvian</option>
      <option value="li">Limburgan; Limburger; Limburgish</option>
      <option value="ln">Lingala</option>
      <option value="lt">Lithuanian</option>
      <option value="lu">Luba-Katanga</option>
      <option value="lb">Luxembourgish; Letzeburgesch</option>
      <option value="mk">Macedonian</option>
      <option value="mg">Malagasy</option>
      <option value="ms">Malay</option>
      <option value="ml">Malayalam</option>
      <option value="mt">Maltese</option>
      <option value="gv">Manx</option>
      <option value="mi">Maori</option>
      <option value="mr">Marathi</option>
      <option value="mh">Marshallese</option>
      <option value="mn">Mongolian</option>
      <option value="na">Nauru</option>
      <option value="nv">Navajo; Navaho</option>
      <option value="nd">Ndebele North; North Ndebele</option>
      <option value="nr">Ndebele South; South Ndebele</option>
      <option value="ng">Ndonga</option>
      <option value="ne">Nepali</option>
      <option value="se">Northern Sami</option>
      <option value="no">Norwegian</option>
      <option value="nn">Norwegian Nynorsk; Nynorsk Norwegian</option>
      <option value="oc">Occitan (post 1500); ProvenÃ§al</option>
      <option value="oj">Ojibwa</option>
      <option value="or">Oriya</option>
      <option value="om">Oromo</option>
      <option value="os">Ossetian; Ossetic</option>
      <option value="pi">Pali</option>
      <option value="pa">Panjabi; Punjabi</option>
      <option value="fa">Persian</option>
      <option value="pl">Polish</option>
      <option value="pt">Portuguese</option>
      <option value="ps">Pushto; Pashto</option>
      <option value="qu">Quechua</option>
      <option value="ro">Romanian; Moldavian; Moldovan</option>
      <option value="rm">Romansh</option>
      <option value="rn">Rundi</option>
      <option value="ru">Russian</option>
      <option value="sm">Samoan</option>
      <option value="sg">Sango</option>
      <option value="sa">Sanskrit</option>
      <option value="sc">Sardinian</option>
      <option value="sr">Serbian</option>
      <option value="sn">Shona</option>
      <option value="ii">Sichuan Yi; Nuosu</option>
      <option value="sd">Sindhi</option>
      <option value="si">Sinhala; Sinhalese</option>
      <option value="sk">Slovak</option>
      <option value="sl">Slovenian</option>
      <option value="so">Somali</option>
      <option value="st">Sotho Southern</option>
      <option value="es">Spanish; Castilian</option>
      <option value="su">Sundanese</option>
      <option value="sw">Swahili</option>
      <option value="ss">Swati</option>
      <option value="sv">Swedish</option>
      <option value="tl">Tagalog</option>
      <option value="ty">Tahitian</option>
      <option value="tg">Tajik</option>
      <option value="ta">Tamil</option>
      <option value="tt">Tatar</option>
      <option value="te">Telugu</option>
      <option value="th">Thai</option>
      <option value="bo">Tibetan</option>
      <option value="ti">Tigrinya</option>
      <option value="to">Tonga (Tonga Islands)</option>
      <option value="ts">Tsonga</option>
      <option value="tn">Tswana</option>
      <option value="tr">Turkish</option>
      <option value="tk">Turkmen</option>
      <option value="tw">Twi</option>
      <option value="ug">Uighur; Uyghur</option>
      <option value="uk">Ukrainian</option>
      <option value="ur">Urdu</option>
      <option value="uz">Uzbek</option>
      <option value="ve">Venda</option>
      <option value="vi">Vietnamese</option>
      <option value="vo">Volapük</option>
      <option value="wa">Walloon</option>
      <option value="cy">Welsh</option>
      <option value="fy">Western Frisian</option>
      <option value="wo">Wolof</option>
      <option value="xh">Xhosa</option>
      <option value="yi">Yiddish</option>
      <option value="yo">Yoruba</option>
      <option value="za">Zhuang; Chuang</option>
      <option value="zu">Zulu</option>
    </select>
  );
}