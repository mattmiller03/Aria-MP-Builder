cd /opt/aria/Aria-MP-Builder

# 1. Show the server's current manifest (is it valid JSON?)
cat Azure-Native-Build/manifest.txt
python3 -c "import json; json.load(open('Azure-Native-Build/manifest.txt')); print('manifest.txt is valid JSON')"

# 2. Show git state (is the server behind/ahead/dirty?)
git status Azure-Native-Build/manifest.txt
git diff Azure-Native-Build/manifest.txt

# 3. Clear images AGAIN for good measure
sudo docker images | grep -iE 'azure|microsoft' | awk '{print $3}' | xargs -r sudo docker rmi --force

# 4. Start the build in the background, then hit the container while it's live
mkdir -p debug
bash scripts/build-pak.sh 2>&1 | tee debug/build.log &
BUILD_PID=$!

# 5. Wait a few seconds for the container to come up, then grab ALL azure container logs
sleep 15
for cid in $(sudo docker ps -a --format '{{.ID}} {{.Image}}' | grep -iE 'azure|microsoft' | awk '{print $1}'); do
  echo "=== container $cid ==="
  sudo docker logs "$cid" 2>&1 | tail -60
  echo ""
done | tee debug/container.log

# 6. Wait for the build to finish
wait $BUILD_PID
echo "=== build exit: $? ==="