# �G���[�������ɃX�N���v�g���~
$ErrorActionPreference = "Stop"

Write-Host "�e�X�g�����Z�b�g�A�b�v���Ă��܂�..." -ForegroundColor Cyan

# �����̃R���e�i���N���[���A�b�v
Write-Host "�����̃R���e�i���N���[���A�b�v���Ă��܂�..." -ForegroundColor Yellow
docker-compose -f docker-compose.test.yml down

# �e�X�g�p�R���e�i���N��
Write-Host "�e�X�g�p�R���e�i���N�����Ă��܂�..." -ForegroundColor Yellow
docker-compose -f docker-compose.test.yml up -d

# �R���e�i�̋N����ҋ@�i���b�j
Write-Host "�R���e�i�̋N����ҋ@���Ă��܂��i5�b�j..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# �e�X�g�����s
Write-Host "�e�X�g�����s���Ă��܂�..." -ForegroundColor Green
docker exec test_app /bin/bash -c "python -m pytest -v"

# �I�����̃N���[���A�b�v
Write-Host "�e�X�g�����N���[���A�b�v���Ă��܂�..." -ForegroundColor Yellow
docker-compose -f docker-compose.test.yml down

Write-Host "�e�X�g���s���������܂���" -ForegroundColor Cyan
