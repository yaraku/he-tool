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

export default function ErrorCategorySelector(props) {
  return (
    <select
      className={props.className}
      disabled={props.disabled}
      onChange={props.onChange}
      value={props.value}
    >
      <optgroup>
        <option id="000" value="000">
          No Error
        </option>
      </optgroup>
      <optgroup label="Accuracy">
        <option id="A01" value="A01">
          A1 &nbsp; Mistranslation
        </option>
        <option id="A02" value="A02">
          A2 &nbsp; Positive/Negative
        </option>
        <option id="A03" value="A03">
          A3 &nbsp; Numbers
        </option>
        <option id="A04" value="A04">
          A4 &nbsp; Pronoun
        </option>
        <option id="A05" value="A05">
          A5 &nbsp; Proper Noun
        </option>
        <option id="A06" value="A06">
          A6 &nbsp; Omission
        </option>
        <option id="A07" value="A07">
          A7 &nbsp; Addition
        </option>
        <option id="A08" value="A08">
          A8 &nbsp; Untranslated
        </option>
        <option id="A09" value="A09">
          A9 &nbsp; Others
        </option>
      </optgroup>
      <optgroup label="Fluency">
        <option id="F01" value="F01">
          F1 &nbsp; Typography/Spelling
        </option>
        <option id="F02" value="F02">
          F2 &nbsp; Wrong Kanji
        </option>
        <option id="F03" value="F03">
          F3 &nbsp; Grammar
        </option>
        <option id="F04" value="F04">
          F4 &nbsp; Misuse
        </option>
        <option id="F05" value="F05">
          F5 &nbsp; Collocation
        </option>
        <option id="F06" value="F06">
          F6 &nbsp; Grammar register
        </option>
        <option id="F07" value="F07">
          F7 &nbsp; Ambiguity
        </option>
        <option id="F08" value="F08">
          F8 &nbsp; Unintelligible
        </option>
        <option id="F09" value="F09">
          F9 &nbsp; Symbols
        </option>
        <option id="F10" value="F10">
          F10 &nbsp; Others
        </option>
      </optgroup>
      <optgroup label="Terminology">
        <option id="T01" value="T01">
          T1 &nbsp; Inconsistent with termbase
        </option>
        <option id="T02" value="T02">
          T2 &nbsp; Inconsistent with domain
        </option>
        <option id="T03" value="T03">
          T3 &nbsp; Inconsistent use
        </option>
        <option id="T04" value="T04">
          T4 &nbsp; Others
        </option>
      </optgroup>
      <optgroup label="Style">
        <option id="S01" value="S01">
          S1 &nbsp; Inconsistent with company style
        </option>
        <option id="S02" value="S02">
          S2 &nbsp; Register
        </option>
        <option id="S03" value="S03">
          S3 &nbsp; Inconsistent style
        </option>
        <option id="S04" value="S04">
          S4 &nbsp; Others
        </option>
      </optgroup>
      <optgroup label="Locale">
        <option id="L01" value="L01">
          L1 &nbsp; Locale convention
        </option>
      </optgroup>
      <optgroup label="SourceError">
        <option id="SE1" value="SE1">
          SE &nbsp; Source Error
        </option>
      </optgroup>
    </select>
  );
}
