rmdir /S /Q dist
uv build
del /Q "endstone\bedrock_server\plugins\*essentialstone*"
move /Y "dist\*.whl" "endstone\bedrock_server\plugins\"

echo batch completed.
