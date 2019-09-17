Formex+CALS Samples
===================

This directory contains Formex samples which contains CALS tables.

For instances:

```xml
<GENERAL xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:noNamespaceSchemaLocation="formex-05.59-20170418_jouve.xd"
         NNC="YES">
  <BIB.INSTANCE>[...]</BIB.INSTANCE>
  <CONTENTS>
    <TBL COLS="2" NO.SEQ="0001">
      <TITLE><TI><P>Table title</P></TI></TITLE>
      <table frame="none" colsep="0" rowsep="0">
        <tgroup cols="2">
          <colspec colname="c1"/>
          <colspec colname="c2"/>
          <thead>
            <row rowstyle="ROW-HEADER">
              <entry>
                <HT TYPE="BOLD">Header 1</HT>
              </entry>
              <entry>
                <HT TYPE="BOLD">Header 2</HT>
              </entry>
            </row>
          </thead>
          <tbody>
            <row>
              <entry>Cell A1</entry>
              <entry>Cell B1</entry>
            </row>
            <row>
              <entry><P>Cell A2</P></entry>
              <entry><P>Cell B2</P></entry>
            </row>
          </tbody>
        </tgroup>
      </table>
    </TBL>
  </CONTENTS>
</GENERAL>
```

**Note:**

The CALS elements and attributes may have a different namespace to simplify
the retro-conversion CALS to Formex.
