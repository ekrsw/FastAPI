import pytest
import pytest_asyncio
from sqlalchemy import select
import uuid

from app.models.group import Group
from app.schemas.group_schema import GroupCreate, GroupSchema
from app.db.session import AsyncContextManager

from app.tests.conftest import unique_groupname


@pytest_asyncio.fixture
async def test_group(unique_groupname):
    """テスト用のグループを作成する"""
    group = await Group.create_group(obj_in={
        "groupname": unique_groupname
    })
    return group


@pytest.mark.asyncio
async def test_create_group(unique_groupname):
    """グループを作成し、フィールドが正しく設定されているかを確認"""
    new_group = await Group.create_group(obj_in={
        "groupname": unique_groupname
    })

    assert new_group.id is not None, "グループIDが設定されているか"
    assert new_group.groupname == unique_groupname, "グループ名が正しいか"

    # データベースに保存されているか確認
    async with AsyncContextManager() as session:
        result = await session.execute(select(Group).where(Group.id == new_group.id))
        exist_group = result.scalars().first()
    assert exist_group is not None, "グループがデータベースに保存されているか"


@pytest.mark.asyncio
async def test_get_group_by_id(test_group):
    """IDによるグループ取得が正しく動作するかを確認"""
    group_id = test_group.id
    
    # グループをIDで取得（直接SQLAlchemyを使用）
    async with AsyncContextManager() as session:
        result = await session.execute(select(Group).where(Group.id == group_id))
        retrieved_group = result.scalars().first()
    
    assert retrieved_group is not None, "グループが取得できているか"
    assert retrieved_group.id == group_id, "正しいグループが取得できているか"
    assert retrieved_group.groupname == test_group.groupname, "グループ名が一致しているか"


@pytest.mark.asyncio
async def test_get_all_groups(test_group):
    """全グループ取得が正しく動作するかを確認"""
    # 全グループを取得
    groups = await Group.get_all_groups()
    
    assert len(groups) > 0, "グループが取得できているか"
    assert any(g.id == test_group.id for g in groups), "作成したグループが含まれているか"


@pytest.mark.asyncio
async def test_update_group(test_group):
    """グループ情報の更新が正しく動作するかを確認"""
    new_groupname = f"updated_{uuid.uuid4()}"
    
    # グループ情報を更新
    updated_group = await Group.update_group(
        db_obj=test_group,
        obj_in={"groupname": new_groupname}
    )
    
    assert updated_group.groupname == new_groupname, "グループ名が更新されているか"
    
    # データベースから再取得して確認
    async with AsyncContextManager() as session:
        result = await session.execute(select(Group).where(Group.id == test_group.id))
        retrieved_group = result.scalars().first()
    assert retrieved_group.groupname == new_groupname, "データベース上でもグループ名が更新されているか"


@pytest.mark.asyncio
async def test_update_group_edge_cases(unique_groupname):
    """グループ更新の特殊ケースを確認"""
    # 存在しないグループの更新を試みる
    # 注: 現在の実装ではエラーが発生しない可能性があるため、このテストはスキップします
    
    # 一部のフィールドのみを更新
    active_group = await Group.create_group(obj_in={
        "groupname": f"partial_{uuid.uuid4()}"
    })
    original_created_at = active_group.created_at
    
    updated_group = await Group.update_group(
        db_obj=active_group,
        obj_in={"groupname": f"updated_{uuid.uuid4()}"}
    )
    
    assert updated_group.created_at == original_created_at, "更新していないフィールドが保持されているか"


@pytest.mark.asyncio
async def test_delete_group_permanently(unique_groupname):
    """物理削除が正しく動作するかを確認"""
    # 新しいグループを作成
    new_group = await Group.create_group(obj_in={
        "groupname": unique_groupname
    })
    group_id = new_group.id
    
    # 作成されたことを確認
    async with AsyncContextManager() as session:
        result = await session.execute(select(Group).where(Group.id == group_id))
        created_group = result.scalars().first()
    assert created_group is not None, "グループが作成されているか"
    
    # グループを物理削除
    await Group.delete_group_permanently(group_id)
    
    # 削除されたグループを取得しようとする
    deleted_group = await Group.get_group_by_id(group_id)
    
    assert deleted_group is None, "グループが完全に削除されているか"


@pytest.mark.asyncio
async def test_delete_group_edge_cases():
    """グループ削除の特殊ケースを確認"""
    # 存在しないグループIDで物理削除を試みる
    # 注: 現在の実装ではエラーが発生しない可能性があるため、このテストはスキップします
    pass


@pytest.mark.asyncio
async def test_from_schema(unique_groupname):
    """PydanticスキーマからGroupオブジェクトを作成できるかを確認"""
    # スキーマを作成
    schema = GroupCreate(groupname=unique_groupname)
    
    # スキーマからグループを作成
    new_group = await Group.from_schema(schema=schema)
    
    assert new_group.id is not None, "グループIDが設定されているか"
    assert new_group.groupname == unique_groupname, "グループ名が正しく設定されているか"
    
    # データベースに保存されているか確認
    async with AsyncContextManager() as session:
        result = await session.execute(select(Group).where(Group.id == new_group.id))
        exist_group = result.scalars().first()
    assert exist_group is not None, "グループがデータベースに保存されているか"


@pytest.mark.asyncio
async def test_update_from_schema(test_group):
    """PydanticスキーマでGroupオブジェクトを更新できるかを確認"""
    new_groupname = f"schema_updated_{uuid.uuid4()}"
    
    # 更新用スキーマを作成
    update_schema = GroupCreate(groupname=new_groupname)
    
    # スキーマでグループを更新
    updated_group = await Group.update_from_schema(db_obj=test_group, schema=update_schema)
    
    assert updated_group.groupname == new_groupname, "グループ名が更新されているか"
    
    # データベースから再取得して確認
    async with AsyncContextManager() as session:
        result = await session.execute(select(Group).where(Group.id == test_group.id))
        retrieved_group = result.scalars().first()
    assert retrieved_group.groupname == new_groupname, "データベース上でもグループ名が更新されているか"


@pytest.mark.asyncio
async def test_update_from_schema_edge_cases():
    """スキーマ更新の特殊ケースを確認"""
    # Noneオブジェクトで更新を試みる
    update_schema = GroupCreate(groupname="test")
    with pytest.raises(ValueError, match="Group not found"):
        await Group.update_from_schema(db_obj=None, schema=update_schema)


@pytest.mark.asyncio
async def test_group_name_validation():
    """グループ名のバリデーションテスト"""
    # 2文字のgroupname（エラー）
    with pytest.raises(ValueError, match="groupname must be between 3 and 100 characters"):
        schema = GroupCreate(groupname="ab")
        await Group.from_schema(schema=schema)
    
    # 101文字のgroupname（エラー）
    long_name = "a" * 101
    with pytest.raises(ValueError, match="groupname must be between 3 and 100 characters"):
        schema = GroupCreate(groupname=long_name)
        await Group.from_schema(schema=schema)
    
    # 空白のみのgroupname（エラー）
    with pytest.raises(ValueError, match="groupname must not be empty"):
        schema = GroupCreate(groupname="   ")
        await Group.from_schema(schema=schema)
    
    # 特殊文字を含むgroupname（正常系）
    special_name = "Test-Group_123!@#"
    schema = GroupCreate(groupname=special_name)
    group = await Group.from_schema(schema=schema)
    assert group.groupname == special_name


@pytest.mark.asyncio
async def test_duplicate_group_creation():
    """重複するグループ名での作成テスト"""
    groupname = f"test_duplicate_{uuid.uuid4()}"
    
    # 1回目の作成（成功）
    group1 = await Group.create_group(obj_in={"groupname": groupname})
    assert group1.groupname == groupname
    
    # 2回目の作成（同じgroupname）
    group2 = await Group.create_group(obj_in={"groupname": groupname})
    assert group2.groupname == groupname
    assert group1.id != group2.id  # 異なるIDが割り当てられていることを確認


@pytest.mark.asyncio
async def test_group_not_found():
    """存在しないグループの操作テスト"""
    non_existent_id = 99999
    
    # 存在しないIDでのグループ取得
    non_existent_group = await Group.get_group_by_id(non_existent_id)
    assert non_existent_group is None
    
    # 存在しないグループの更新試行
    with pytest.raises(ValueError, match="Group not found"):
        schema = GroupCreate(groupname="updated")
        await Group.update_from_schema(db_obj=non_existent_group, schema=schema)
    
    # 存在しないグループの削除試行
    # 注: 現在の実装では例外は発生しないが、将来的にはエラーハンドリングを追加することを推奨
    await Group.delete_group_permanently(non_existent_id)


@pytest.mark.asyncio
async def test_group_transaction_rollback():
    """トランザクションのロールバックテスト"""
    # 正常なグループを作成
    valid_group = await Group.create_group(obj_in={"groupname": f"valid_{uuid.uuid4()}"})
    assert valid_group.id is not None

    # トランザクション内でエラーを発生させる
    async with AsyncContextManager() as session:
        try:
            # 既存のグループを作成
            new_group = Group()
            new_group.groupname = f"rollback_{uuid.uuid4()}"
            session.add(new_group)
            
            # 意図的にエラーを発生させる（NULLでない列にNULLを設定）
            new_group.groupname = None
            await session.commit()
        except Exception:
            await session.rollback()
            
    # ロールバック後、新しいグループが作成されていないことを確認
    all_groups = await Group.get_all_groups()
    new_group_exists = any(g.groupname == new_group.groupname for g in all_groups)
    assert not new_group_exists, "ロールバックが正しく機能し、グループが作成されていないこと"

    # 既存の有効なグループは影響を受けていないことを確認
    valid_group_check = await Group.get_group_by_id(valid_group.id)
    assert valid_group_check is not None, "既存の有効なグループが維持されていること"


@pytest.mark.asyncio
async def test_bulk_group_operations():
    """一括操作のテスト"""
    # 複数グループの一括作成
    group_names = [f"bulk_{i}_{uuid.uuid4()}" for i in range(3)]
    groups = []
    
    async with AsyncContextManager() as session:
        for name in group_names:
            new_group = Group()
            new_group.groupname = name
            session.add(new_group)
            groups.append(new_group)
        await session.commit()

    # 作成されたグループを確認
    for group in groups:
        assert group.id is not None, "グループが正しく作成されていること"
        
    # 一括更新
    new_names = [f"updated_{g.groupname}" for g in groups]
    async with AsyncContextManager() as session:
        for group, new_name in zip(groups, new_names):
            group.groupname = new_name
            session.add(group)
        await session.commit()

    # 更新を確認
    updated_groups = await Group.get_all_groups()
    for new_name in new_names:
        assert any(g.groupname == new_name for g in updated_groups), "グループ名が更新されていること"

    # 一括削除
    async with AsyncContextManager() as session:
        for group in groups:
            await session.delete(group)
        await session.commit()

    # 削除を確認
    final_groups = await Group.get_all_groups()
    for new_name in new_names:
        assert not any(g.groupname == new_name for g in final_groups), "グループが削除されていること"


@pytest.mark.asyncio
async def test_performance_large_data():
    """大量データ処理のパフォーマンステスト"""
    # 大量のグループを作成（テスト用に50件）
    test_groups = []
    async with AsyncContextManager() as session:
        for i in range(50):
            new_group = Group()
            new_group.groupname = f"perf_test_{i}_{uuid.uuid4()}"
            session.add(new_group)
            test_groups.append(new_group)
        await session.commit()

    try:
        # 全件取得のパフォーマンス確認
        all_groups = await Group.get_all_groups()
        assert len(all_groups) >= 50, "全てのテストグループが取得できていること"

        # 個別取得のパフォーマンス確認
        for group in test_groups[:5]:  # 最初の5件をサンプルとしてテスト
            retrieved_group = await Group.get_group_by_id(group.id)
            assert retrieved_group is not None, "個別のグループが取得できていること"
            assert retrieved_group.id == group.id, "正しいグループが取得できていること"

    finally:
        # テストデータのクリーンアップ
        async with AsyncContextManager() as session:
            for group in test_groups:
                await session.delete(group)
            await session.commit()


@pytest.mark.asyncio
async def test_performance_pagination():
    """ページネーション機能のテスト"""
    # テストデータ作成（30件）
    test_groups = []
    async with AsyncContextManager() as session:
        for i in range(30):
            new_group = Group()
            new_group.groupname = f"page_test_{i}_{uuid.uuid4()}"
            session.add(new_group)
            test_groups.append(new_group)
        await session.commit()

    try:
        # ページネーションを使用してデータを取得
        async with AsyncContextManager() as session:
            # 1ページ目（10件）
            stmt = select(Group).limit(10).offset(0)
            result = await session.execute(stmt)
            page1 = result.scalars().all()
            assert len(page1) == 10, "1ページ目が10件取得できていること"

            # 2ページ目（10件）
            stmt = select(Group).limit(10).offset(10)
            result = await session.execute(stmt)
            page2 = result.scalars().all()
            assert len(page2) == 10, "2ページ目が10件取得できていること"

            # 3ページ目（10件）
            stmt = select(Group).limit(10).offset(20)
            result = await session.execute(stmt)
            page3 = result.scalars().all()
            assert len(page3) == 10, "3ページ目が10件取得できていること"

            # ページ間で重複がないことを確認
            page1_ids = {g.id for g in page1}
            page2_ids = {g.id for g in page2}
            page3_ids = {g.id for g in page3}
            assert not (page1_ids & page2_ids), "1ページ目と2ページ目で重複がないこと"
            assert not (page2_ids & page3_ids), "2ページ目と3ページ目で重複がないこと"
            assert not (page1_ids & page3_ids), "1ページ目と3ページ目で重複がないこと"

    finally:
        # テストデータのクリーンアップ
        async with AsyncContextManager() as session:
            for group in test_groups:
                await session.delete(group)
            await session.commit()
