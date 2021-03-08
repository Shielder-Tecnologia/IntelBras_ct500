cd /d %~dp0
if /i "%PROCESSOR_IDENTIFIER:~0,3%"=="X86" (
	
	copy .\32\*.dll %windir%\system32\
	regsvr32 %windir%\system32\zkemkeeper.dll
	) else (
		
		copy .\64\*.dll %windir%\SysWOW64\
		regsvr32 %windir%\SysWOW64\zkemkeeper.dll
	)
exit